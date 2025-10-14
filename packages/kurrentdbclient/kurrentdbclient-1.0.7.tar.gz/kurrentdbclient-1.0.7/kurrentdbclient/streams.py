from __future__ import annotations

import contextlib
import datetime
import math
import sys
from abc import abstractmethod
from asyncio import CancelledError
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, overload, runtime_checkable
from uuid import UUID, uuid4

import grpc
import grpc.aio
from google.protobuf import duration_pb2, empty_pb2
from grpc.aio import AioRpcError, UsageError
from typing_extensions import Literal, Protocol

from kurrentdbclient.common import (
    DEFAULT_CHECKPOINT_INTERVAL_MULTIPLIER,
    DEFAULT_WINDOW_SIZE,
    PROTOBUF_MAX_DEADLINE_SECONDS,
    AbstractAsyncCatchupSubscription,
    AbstractAsyncReadResponse,
    AbstractCatchupSubscription,
    AbstractReadResponse,
    AsyncGrpcStreamer,
    AsyncGrpcStreamers,
    GrpcStreamer,
    GrpcStreamers,
    KurrentDBService,
    Metadata,
    TGrpcStreamers,
    construct_filter_exclude_regex,
    construct_filter_include_regex,
    construct_recorded_event,
    handle_rpc_error,
)
from kurrentdbclient.events import (
    CaughtUp,
    Checkpoint,
    FellBehind,
    NewEvent,
    RecordedEvent,
)
from kurrentdbclient.exceptions import (
    AccessDeniedError,
    AppendDeadlineExceededError,
    BadRequestError,
    CancelledByClientError,
    InvalidTransactionError,
    KurrentDBClientError,
    MaximumAppendSizeExceededError,
    NotFoundError,
    StreamIsDeletedError,
    SubscriptionConfirmationError,
    UnknownError,
    WrongCurrentVersionError,
)
from kurrentdbclient.protos.Grpc import (
    shared_pb2,
    status_pb2,
    streams_pb2,
    streams_pb2_grpc,
)

if TYPE_CHECKING:
    from google.protobuf.timestamp_pb2 import Timestamp

    from kurrentdbclient.connection_spec import ConnectionSpec


@runtime_checkable
class _ReadResps(Iterator[streams_pb2.ReadResp], Protocol):
    @abstractmethod
    def cancel(self) -> None:  # pragma: no cover
        ...


# @runtime_checkable
# class _BatchAppendResps(Iterator[streams_pb2.BatchAppendResp], Protocol):
#     @abstractmethod
#     def cancel(self) -> None:
#         ...  # pragma: no cover
#
#
class StreamState(Enum):
    ANY = "ANY"
    NO_STREAM = "NO_STREAM"
    EXISTS = "EXISTS"


class BaseReadResponse:
    def __init__(
        self,
        stream_name: str | None,
    ):
        self._stream_name = stream_name
        self._include_checkpoints = False
        self._include_caught_up = False
        self._include_fell_behind = False

    def _convert_read_resp(
        self, read_resp: streams_pb2.ReadResp
    ) -> RecordedEvent | None:
        content_oneof = read_resp.WhichOneof("content")
        if content_oneof == "stream_not_found":
            msg = f"Stream {self._stream_name!r} not found"
            raise NotFoundError(msg)
        if content_oneof == "event":
            return construct_recorded_event(read_resp.event)
        if content_oneof == "checkpoint":
            checkpoint = read_resp.checkpoint
            return Checkpoint(
                commit_position=checkpoint.commit_position,
                prepare_position=checkpoint.prepare_position,
                recorded_at=self._convert_timestamp(checkpoint.timestamp),
            )
        if content_oneof == "caught_up":
            caught_up = read_resp.caught_up
            return CaughtUp(
                stream_position=caught_up.stream_revision,
                commit_position=caught_up.position.commit_position,
                prepare_position=caught_up.position.prepare_position,
                recorded_at=self._convert_timestamp(caught_up.timestamp),
            )
        if content_oneof == "fell_behind":
            fell_behind = read_resp.fell_behind
            return FellBehind(
                stream_position=fell_behind.stream_revision,
                commit_position=fell_behind.position.commit_position,
                prepare_position=fell_behind.position.prepare_position,
                recorded_at=self._convert_timestamp(fell_behind.timestamp),
            )
        return None
        # Todo: Maybe support other content_oneof values:
        # 		uint64 first_stream_position = 5;
        # 		uint64 last_stream_position = 6;
        # 		AllStreamPosition last_all_stream_position = 7;
        #
        # Todo: Not sure how to request to get first_stream_position,
        #   last_stream_position, first_all_stream_position.

    def _convert_timestamp(self, timestamp: Timestamp) -> datetime.datetime | None:
        if timestamp.seconds == 0 and timestamp.nanos == 0:
            return None
        return timestamp.ToDatetime(datetime.timezone.utc)

    def _filter_recorded_event(
        self, recorded_event: RecordedEvent | None
    ) -> RecordedEvent | None:
        recorded_event_type = type(recorded_event)
        if (
            (recorded_event_type is RecordedEvent)
            or (self._include_checkpoints and recorded_event_type is Checkpoint)
            or (self._include_caught_up and (recorded_event_type is CaughtUp))
            or (self._include_fell_behind and (recorded_event_type is FellBehind))
        ):
            return recorded_event
        return None


class AsyncReadResponse(BaseReadResponse, AsyncGrpcStreamer, AbstractAsyncReadResponse):
    def __init__(
        self,
        aio_call: grpc.aio.UnaryStreamCall[streams_pb2.ReadReq, streams_pb2.ReadResp],
        stream_name: str | None,
        grpc_streamers: AsyncGrpcStreamers,
    ):
        BaseReadResponse.__init__(self, stream_name=stream_name)
        AsyncGrpcStreamer.__init__(self, grpc_streamers=grpc_streamers)
        AbstractAsyncReadResponse.__init__(self)
        self.aio_call = aio_call
        self.read_resp_iter = aio_call.__aiter__()

    async def __anext__(self) -> RecordedEvent:
        try:
            while True:
                read_resp = await self._get_next_read_resp()
                recorded_event = self._filter_recorded_event(
                    self._convert_read_resp(read_resp)
                )
                if recorded_event is not None:
                    return recorded_event
        except CancelledByClientError:
            await self.stop()
            raise StopAsyncIteration from None
        except:
            await self.stop()
            raise

    async def _get_next_read_resp(self) -> streams_pb2.ReadResp:
        try:
            read_resp = await self.read_resp_iter.__anext__()
            if self._has_iter_error_for_testing():
                raise AioRpcError(
                    grpc.StatusCode.INTERNAL,
                    grpc.aio.Metadata(),
                    grpc.aio.Metadata(),
                    "",
                    "",
                )
        except grpc.RpcError as e:
            raise handle_streams_rpc_error(e) from None
        except CancelledError:
            raise CancelledByClientError from None
        else:
            assert isinstance(read_resp, streams_pb2.ReadResp)
            return read_resp

    async def stop(self) -> None:
        if not await self._set_is_stopped():
            # Get a UsageError (when testing) by closing
            # channel and then canceling a call.
            with contextlib.suppress(UsageError):
                self.aio_call.cancel()
            self._grpc_streamers.remove(self)


class AsyncCatchupSubscription(AsyncReadResponse, AbstractAsyncCatchupSubscription):
    def __init__(
        self,
        *,
        aio_call: grpc.aio.UnaryStreamCall[streams_pb2.ReadReq, streams_pb2.ReadResp],
        stream_name: str | None,
        grpc_streamers: AsyncGrpcStreamers,
        include_checkpoints: bool = False,
        include_caught_up: bool = False,
        include_fell_behind: bool = False,
    ):
        super().__init__(
            aio_call=aio_call, stream_name=stream_name, grpc_streamers=grpc_streamers
        )
        self._include_checkpoints = include_checkpoints
        self._include_caught_up = include_caught_up
        self._include_fell_behind = include_fell_behind

    async def check_confirmation(self) -> None:
        read_resp = await self._get_next_read_resp()
        content_oneof = read_resp.WhichOneof("content")
        if content_oneof != "confirmation":  # pragma: no cover
            msg = f"Expected subscription confirmation, got: {read_resp}"
            raise SubscriptionConfirmationError(msg)
        self._subscription_id = read_resp.confirmation.subscription_id

    @property
    def subscription_id(self) -> str:
        return self._subscription_id


class ReadResponse(GrpcStreamer, BaseReadResponse, AbstractReadResponse):
    def __init__(
        self,
        read_resps: _ReadResps,
        stream_name: str | None,
        grpc_streamers: GrpcStreamers,
    ):
        GrpcStreamer.__init__(self, grpc_streamers=grpc_streamers)
        BaseReadResponse.__init__(self, stream_name=stream_name)
        AbstractReadResponse.__init__(self)
        self._read_resps = read_resps

    def __next__(self) -> RecordedEvent:
        try:
            while True:
                read_resp = self._get_next_read_resp()
                recorded_event = self._filter_recorded_event(
                    self._convert_read_resp(read_resp)
                )
                if recorded_event is not None:
                    return recorded_event
        except CancelledByClientError:
            self.stop()
            raise StopIteration from None
        except:
            self.stop()
            raise

    def _get_next_read_resp(self) -> streams_pb2.ReadResp:
        try:
            read_resp = next(self._read_resps)
        except grpc.RpcError as e:
            raise handle_streams_rpc_error(e) from None
        else:
            assert isinstance(read_resp, streams_pb2.ReadResp)
            return read_resp

    def stop(self) -> None:
        if not self._set_is_stopped():
            self._read_resps.cancel()
            self._grpc_streamers.remove(self)


class CatchupSubscription(ReadResponse, AbstractCatchupSubscription):
    def __init__(
        self,
        *,
        read_resps: _ReadResps,
        stream_name: str | None,
        grpc_streamers: GrpcStreamers,
        include_checkpoints: bool = False,
        include_caught_up: bool = False,
        include_fell_behind: bool = False,
    ):
        super().__init__(
            read_resps=read_resps,
            stream_name=stream_name,
            grpc_streamers=grpc_streamers,
        )
        self._include_checkpoints = include_checkpoints
        self._include_caught_up = include_caught_up
        self._include_fell_behind = include_fell_behind
        try:
            first_read_resp = self._get_next_read_resp()
            content_oneof = first_read_resp.WhichOneof("content")
            if content_oneof == "confirmation":
                self._subscription_id = first_read_resp.confirmation.subscription_id
            else:  # pragma: no cover
                msg = f"Expected subscription confirmation, got: {first_read_resp}"
                raise SubscriptionConfirmationError(msg)
        except Exception:
            self.stop()
            raise

    @property
    def subscription_id(self) -> str:
        return self._subscription_id


@dataclass
class BatchAppendResponse:
    commit_position: int


# @dataclass
# class BatchAppendRequest:
#     stream_name: str
#     current_version: Union[int, StreamState]
#     events: Iterable[NewEvent]
#     correlation_id: UUID = field(default_factory=uuid4)
#     deadline: int = PROTOBUF_MAX_DEADLINE_SECONDS
#
#
# if TYPE_CHECKING:  # pragma: no cover
#
#     class _BatchAppendFuture(Future[BatchAppendResponse]):
#         pass
#
# else:
#
#     class _BatchAppendFuture(Future):
#         pass
#
#
# class BatchAppendFuture(_BatchAppendFuture):
#    def __init__(self, batch_append_request: BatchAppendRequest):
#        super().__init__()
#        self.batch_append_request = batch_append_request
#
#
# if TYPE_CHECKING:  # pragma: no cover
#    BatchAppendFutureQueue = Queue[BatchAppendFuture]
# else:
#    BatchAppendFutureQueue = Queue
#
#
# class BatchAppendFutureIterator(Iterator[streams_pb2.BatchAppendReq]):
#     def __init__(self, queue: BatchAppendFutureQueue):
#         self.queue = queue
#         self.futures_by_correlation_id: Dict[UUID, BatchAppendFuture] = {}
#
#     def __next__(self) -> streams_pb2.BatchAppendReq:
#         future = self.queue.get()
#         batch = future.batch_append_request
#         self.futures_by_correlation_id[batch.correlation_id] = future
#         return BaseStreamsService._construct_batch_append_req(
#             stream_name=batch.stream_name,
#             current_version=batch.current_version,
#             events=batch.events,
#             # timeout=batch.timeout,
#             correlation_id=batch.correlation_id,
#         )
#
#     def pop_future(self, correlation_id: UUID) -> BatchAppendFuture:
#         return self.futures_by_correlation_id.pop(correlation_id)
#
#     def __del__(self) -> None:
#         print("DEL BatchAppendFutureIterator")
#
#
# class BatchAppendResps(GrpcStreamer):
#     def __init__(
#         self, batch_append_resps: _BatchAppendResps, grpc_streamers: GrpcStreamers
#     ):
#         grpc_streamers[id(self)] = self
#         self._batch_append_resps = batch_append_resps
#         self._grpc_streamers = grpc_streamers
#         self._is_stopped = False
#
#     def __iter__(self) -> BatchAppendResps:
#         return self
#
#     def __next__(self) -> streams_pb2.BatchAppendResp:
#         try:
#             return next(self._batch_append_resps)
#         except Exception:
#             self.stop()
#             raise
#
#     def stop(self) -> None:
#         if not self._is_stopped:
#             self._batch_append_resps.cancel()
#             try:
#                 self._grpc_streamers.pop(id(self))
#             except KeyError:  # pragma: no cover
#                 pass
#             self._is_stopped = True
#
#     def __del__(self) -> None:
#         self.stop()
#         del self


class BaseStreamsService(KurrentDBService[TGrpcStreamers]):
    def __init__(
        self,
        grpc_channel: grpc.Channel | grpc.aio.Channel,
        connection_spec: ConnectionSpec,
        grpc_streamers: TGrpcStreamers,
    ):
        super().__init__(connection_spec=connection_spec, grpc_streamers=grpc_streamers)
        self._stub = streams_pb2_grpc.StreamsStub(grpc_channel)  # type: ignore[no-untyped-call]

    @staticmethod
    def _generate_append_reqs(
        stream_name: str,
        current_version: int | StreamState,
        events: Iterable[NewEvent],
    ) -> Iterator[streams_pb2.AppendReq]:
        # First, define append request that has 'content' as 'options'.
        options = streams_pb2.AppendReq.Options(
            stream_identifier=shared_pb2.StreamIdentifier(
                stream_name=stream_name.encode("utf8")
            )
        )
        # Decide 'expected_stream_revision'.
        if isinstance(current_version, int):
            assert current_version >= 0
            options.revision = current_version
        else:
            assert isinstance(current_version, StreamState)
            if current_version is StreamState.EXISTS:
                options.stream_exists.CopyFrom(shared_pb2.Empty())
            elif current_version is StreamState.ANY:
                options.any.CopyFrom(shared_pb2.Empty())
            else:
                assert current_version is StreamState.NO_STREAM
                options.no_stream.CopyFrom(shared_pb2.Empty())

        yield streams_pb2.AppendReq(options=options)

        # Secondly, define append requests that has 'content' as 'proposed_message'.
        for event in events:
            proposed_message = streams_pb2.AppendReq.ProposedMessage(
                id=shared_pb2.UUID(string=str(event.id)),
                metadata={"type": event.type, "content-type": event.content_type},
                custom_metadata=event.metadata,
                data=event.data,
            )
            yield streams_pb2.AppendReq(proposed_message=proposed_message)

    @staticmethod
    def _construct_batch_append_req(
        stream_name: str,
        current_version: int | StreamState,
        events: Iterable[NewEvent],
        correlation_id: UUID,
        timeout: float | None = None,
    ) -> streams_pb2.BatchAppendReq:
        # Construct batch request 'options'.
        stream_identifier = shared_pb2.StreamIdentifier(
            stream_name=stream_name.encode("utf8")
        )
        if timeout is not None:
            timeout_split = math.modf(timeout)
            duration_seconds = min(int(timeout_split[1]), PROTOBUF_MAX_DEADLINE_SECONDS)
            duration_nanos = int(timeout_split[0] * 1000000000)
        else:
            duration_seconds = PROTOBUF_MAX_DEADLINE_SECONDS
            duration_nanos = 0
        duration = duration_pb2.Duration(
            seconds=duration_seconds,
            nanos=duration_nanos,
        )
        options = streams_pb2.BatchAppendReq.Options(
            stream_identifier=stream_identifier,
            deadline=duration,
        )
        # Decide options 'expected_stream_revision'.
        if isinstance(current_version, int):
            assert current_version >= 0
            options.stream_position = current_version
        else:
            assert isinstance(current_version, StreamState)
            if current_version is StreamState.EXISTS:
                options.stream_exists.CopyFrom(empty_pb2.Empty())
            elif current_version is StreamState.ANY:
                options.any.CopyFrom(empty_pb2.Empty())
            else:
                assert current_version is StreamState.NO_STREAM
                options.no_stream.CopyFrom(empty_pb2.Empty())

        # Construct batch request 'proposed_messages'.
        # Todo: Split batch.events into chunks of 20?
        proposed_messages = []
        for event in events:
            proposed_message = streams_pb2.BatchAppendReq.ProposedMessage(
                id=shared_pb2.UUID(string=str(event.id)),
                metadata={"type": event.type, "content-type": event.content_type},
                custom_metadata=event.metadata,
                data=event.data,
            )
            proposed_messages.append(proposed_message)
        return streams_pb2.BatchAppendReq(
            correlation_id=shared_pb2.UUID(string=str(correlation_id)),
            options=options,
            proposed_messages=proposed_messages,
            is_final=True,  # This specifies the end of an atomic transaction.
        )

    @staticmethod
    def _convert_batch_append_resp(
        response: streams_pb2.BatchAppendResp,
        stream_name: str,
        current_version: int | StreamState,
    ) -> int:
        # Response 'result' is either 'success' or 'error'.
        result_oneof = response.WhichOneof("result")
        if result_oneof == "success":
            # Return commit position.
            return response.success.position.commit_position

        # Construct exception object.
        assert result_oneof == "error", result_oneof
        assert isinstance(response.error, status_pb2.Status)

        error_details = response.error.details
        if error_details.Is(shared_pb2.WrongExpectedVersion.DESCRIPTOR):
            wrong_version = shared_pb2.WrongExpectedVersion()
            error_details.Unpack(wrong_version)

            csro_oneof = wrong_version.WhichOneof("current_stream_revision_option")
            if csro_oneof == "current_no_stream":
                msg = f"Stream {stream_name!r} does not exist"
                raise WrongCurrentVersionError(msg)
            assert csro_oneof == "current_stream_revision"
            msg = (
                f"Stream position of last event is"
                f" {wrong_version.current_stream_revision}"
                f" not {current_version}"
            )
            raise WrongCurrentVersionError(msg)

        # Todo: Write tests to cover all of this:
        if error_details.Is(shared_pb2.AccessDenied.DESCRIPTOR):  # pragma: no cover
            raise AccessDeniedError
        if error_details.Is(shared_pb2.StreamDeleted.DESCRIPTOR):
            stream_deleted = shared_pb2.StreamDeleted()
            error_details.Unpack(stream_deleted)
            # Todo: Ask DB team if this is ever different from request value.
            # stream_name = stream_deleted.stream_identifier.stream_name
            msg = f"Stream {stream_name !r} is deleted"
            raise StreamIsDeletedError(msg)
        if error_details.Is(shared_pb2.Timeout.DESCRIPTOR):  # pragma: no cover
            raise AppendDeadlineExceededError
        if error_details.Is(shared_pb2.Unknown.DESCRIPTOR):  # pragma: no cover
            raise UnknownError
        if error_details.Is(
            shared_pb2.InvalidTransaction.DESCRIPTOR
        ):  # pragma: no cover
            raise InvalidTransactionError
        if error_details.Is(
            shared_pb2.MaximumAppendSizeExceeded.DESCRIPTOR
        ):  # pragma: no cover
            size_exceeded = shared_pb2.MaximumAppendSizeExceeded()
            error_details.Unpack(size_exceeded)
            size = size_exceeded.maxAppendSize
            msg = f"Max size is {size}"
            raise MaximumAppendSizeExceededError(msg)
        if error_details.Is(shared_pb2.BadRequest.DESCRIPTOR):  # pragma: no cover
            bad_request = shared_pb2.BadRequest()
            error_details.Unpack(bad_request)
            msg = f"Bad request: {bad_request.message}"
            raise BadRequestError(msg)
        # Unexpected error details type.
        raise KurrentDBClientError(error_details)  # pragma: no cover

    @staticmethod
    def _construct_read_request(
        *,
        stream_name: str | None = None,
        stream_position: int | None = None,
        commit_position: int | None = None,
        from_end: bool = False,
        backwards: bool = False,
        resolve_links: bool = False,
        filter_exclude: Sequence[str] = (),
        filter_include: Sequence[str] = (),
        filter_by_stream_name: bool = False,
        limit: int = sys.maxsize,
        subscribe: bool = False,
        window_size: int = DEFAULT_WINDOW_SIZE,
        checkpoint_interval_multiplier: int = DEFAULT_CHECKPOINT_INTERVAL_MULTIPLIER,
    ) -> streams_pb2.ReadReq:
        # Construct ReadReq.Options.
        options = streams_pb2.ReadReq.Options()

        # Decide 'stream_option'.
        if isinstance(stream_name, str):
            assert isinstance(stream_name, str)
            assert commit_position is None
            stream_options = streams_pb2.ReadReq.Options.StreamOptions(
                stream_identifier=shared_pb2.StreamIdentifier(
                    stream_name=stream_name.encode("utf8")
                ),
                revision=stream_position or 0,
            )

            # Decide 'revision_option'.
            if stream_position is not None:
                stream_options.revision = stream_position
            elif from_end is True:
                stream_options.end.CopyFrom(shared_pb2.Empty())
            elif backwards is False:
                stream_options.start.CopyFrom(shared_pb2.Empty())
            else:
                stream_options.end.CopyFrom(shared_pb2.Empty())
            options.stream.CopyFrom(stream_options)
        else:
            assert stream_position is None
            if commit_position is not None:
                all_options = streams_pb2.ReadReq.Options.AllOptions(
                    position=streams_pb2.ReadReq.Options.Position(
                        commit_position=commit_position,
                        # prepare_position=prepare_position or commit_position,
                        prepare_position=commit_position,
                    )
                )
            elif backwards or from_end:
                all_options = streams_pb2.ReadReq.Options.AllOptions(
                    end=shared_pb2.Empty()
                )
            else:
                all_options = streams_pb2.ReadReq.Options.AllOptions(
                    start=shared_pb2.Empty()
                )
            options.all.CopyFrom(all_options)

        # Decide 'read_direction'.
        if backwards is False:
            options.read_direction = streams_pb2.ReadReq.Options.Forwards
        else:
            options.read_direction = streams_pb2.ReadReq.Options.Backwards

        # Decide 'resolve_links'.
        options.resolve_links = resolve_links

        # Decide 'count_option'.
        if subscribe:
            subscription = streams_pb2.ReadReq.Options.SubscriptionOptions()
            options.subscription.CopyFrom(subscription)

        else:
            options.count = limit

        # Decide 'filter_option'.
        if filter_exclude or filter_include:
            filter_options = streams_pb2.ReadReq.Options.FilterOptions(
                max=window_size,
                checkpointIntervalMultiplier=checkpoint_interval_multiplier,
            )

            # Decide 'expression'
            if filter_include:
                regex = construct_filter_include_regex(filter_include)
            else:
                regex = construct_filter_exclude_regex(filter_exclude)

            expression = streams_pb2.ReadReq.Options.FilterOptions.Expression(
                regex=regex
            )

            if filter_by_stream_name:
                filter_options.stream_identifier.CopyFrom(expression)
            else:
                filter_options.event_type.CopyFrom(expression)

            options.filter.CopyFrom(filter_options)
        else:
            options.no_filter.CopyFrom(shared_pb2.Empty())

        # Decide 'uuid_option'.
        options.uuid_option.CopyFrom(
            streams_pb2.ReadReq.Options.UUIDOption(string=shared_pb2.Empty())
        )

        # Decide 'control_option'.
        # Todo: What does this do, and what value should it have?

        return streams_pb2.ReadReq(options=options)

    @staticmethod
    def _construct_delete_req(
        stream_name: str, current_version: int | StreamState
    ) -> streams_pb2.DeleteReq:
        options = streams_pb2.DeleteReq.Options(
            stream_identifier=shared_pb2.StreamIdentifier(
                stream_name=stream_name.encode("utf8")
            )
        )
        # Decide 'expected_stream_revision'.
        if isinstance(current_version, int):
            assert current_version >= 0
            options.revision = current_version
        else:
            assert isinstance(current_version, StreamState)
            if current_version is StreamState.EXISTS:
                options.stream_exists.CopyFrom(shared_pb2.Empty())
            elif current_version is StreamState.ANY:
                options.any.CopyFrom(shared_pb2.Empty())
            else:
                assert current_version is StreamState.NO_STREAM
                options.no_stream.CopyFrom(shared_pb2.Empty())

        return streams_pb2.DeleteReq(options=options)

    @staticmethod
    def _construct_tombstone_req(
        stream_name: str, current_version: int | StreamState
    ) -> streams_pb2.TombstoneReq:
        options = streams_pb2.TombstoneReq.Options(
            stream_identifier=shared_pb2.StreamIdentifier(
                stream_name=stream_name.encode("utf8")
            )
        )
        # Decide 'expected_stream_revision'.
        if isinstance(current_version, int):
            assert current_version >= 0
            # Stream position is expected to be a certain value.
            options.revision = current_version
        else:
            assert isinstance(current_version, StreamState)
            if current_version is StreamState.EXISTS:
                options.stream_exists.CopyFrom(shared_pb2.Empty())
            elif current_version is StreamState.ANY:
                options.any.CopyFrom(shared_pb2.Empty())
            else:
                assert current_version is StreamState.NO_STREAM
                options.no_stream.CopyFrom(shared_pb2.Empty())
        return streams_pb2.TombstoneReq(options=options)


class AsyncStreamsService(BaseStreamsService[AsyncGrpcStreamers]):
    async def batch_append(
        self,
        stream_name: str,
        current_version: int | StreamState,
        events: Iterable[NewEvent],
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> int:
        # Call the gRPC method.
        try:
            req = self._construct_batch_append_req(
                stream_name=stream_name,
                current_version=current_version,
                events=events,
                timeout=timeout,
                correlation_id=uuid4(),
            )
            batch_append_call = self._stub.BatchAppend(
                iter([req]),
                timeout=timeout,
                metadata=self._metadata(metadata, requires_leader=True),
                credentials=credentials,
            )

            async for response in batch_append_call:
                assert isinstance(response, streams_pb2.BatchAppendResp)
                batch_append_response = self._convert_batch_append_resp(
                    response, stream_name, current_version
                )
                batch_append_call.cancel()
                return batch_append_response

            # no cover: start
            msg = "Batch append response not received"
            raise KurrentDBClientError(msg)
            # no cover: stop

        except grpc.RpcError as e:
            raise handle_rpc_error(e) from None

    @overload
    async def read(
        self,
        *,
        stream_name: str | None = None,
        stream_position: int | None = None,
        backwards: bool = False,
        resolve_links: bool = False,
        limit: int = sys.maxsize,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> AsyncReadResponse:
        """
        Signature for reading events from a stream.
        """

    @overload
    async def read(
        self,
        *,
        stream_name: str | None = None,
        stream_position: int | None = None,
        from_end: bool = False,
        resolve_links: bool = False,
        subscribe: Literal[True],
        include_caught_up: bool = False,
        include_fell_behind: bool = False,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> AsyncCatchupSubscription:
        """
        Signature for reading events from a stream with a catch-up subscription.
        """

    @overload
    async def read(
        self,
        *,
        commit_position: int | None = None,
        backwards: bool = False,
        resolve_links: bool = False,
        filter_exclude: Sequence[str] = (),
        filter_include: Sequence[str] = (),
        filter_by_stream_name: bool = False,
        limit: int = sys.maxsize,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> AsyncReadResponse:
        """
        Signature for reading all events.
        """

    @overload
    async def read(
        self,
        *,
        commit_position: int | None = None,
        from_end: bool = False,
        resolve_links: bool = False,
        filter_exclude: Sequence[str] = (),
        filter_include: Sequence[str] = (),
        filter_by_stream_name: bool = False,
        subscribe: Literal[True],
        include_checkpoints: bool = False,
        window_size: int = DEFAULT_WINDOW_SIZE,
        checkpoint_interval_multiplier: int = DEFAULT_CHECKPOINT_INTERVAL_MULTIPLIER,
        include_caught_up: bool = False,
        include_fell_behind: bool = False,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> AsyncCatchupSubscription:
        """
        Signature for reading all events with a catch-up subscription.
        """

    async def read(
        self,
        *,
        stream_name: str | None = None,
        stream_position: int | None = None,
        commit_position: int | None = None,
        from_end: bool = False,
        backwards: bool = False,
        resolve_links: bool = False,
        filter_exclude: Sequence[str] = (),
        filter_include: Sequence[str] = (),
        filter_by_stream_name: bool = False,
        limit: int = sys.maxsize,
        subscribe: bool = False,
        include_checkpoints: bool = False,
        window_size: int = DEFAULT_WINDOW_SIZE,
        checkpoint_interval_multiplier: int = DEFAULT_CHECKPOINT_INTERVAL_MULTIPLIER,
        include_caught_up: bool = False,
        include_fell_behind: bool = False,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> AsyncReadResponse | AsyncCatchupSubscription:
        """
        Constructs and sends a gRPC 'ReadReq' to the 'Read' rpc.

        Returns a generator which yields RecordedEvent objects.
        """

        # Construct read request.
        read_req = self._construct_read_request(
            stream_name=stream_name,
            stream_position=stream_position,
            commit_position=commit_position,
            from_end=from_end,
            backwards=backwards,
            resolve_links=resolve_links,
            filter_exclude=filter_exclude,
            filter_include=filter_include,
            filter_by_stream_name=filter_by_stream_name,
            limit=limit,
            subscribe=subscribe,
            window_size=window_size,
            checkpoint_interval_multiplier=checkpoint_interval_multiplier,
        )

        # Send the read request, and iterate over the response.
        unary_stream_call: grpc.aio.UnaryStreamCall[
            streams_pb2.ReadReq, streams_pb2.ReadResp
        ] = self._stub.Read(
            read_req,
            timeout=timeout,
            metadata=self._metadata(metadata),
            credentials=credentials,
        )

        if not subscribe:
            response = AsyncReadResponse(
                aio_call=unary_stream_call,
                stream_name=stream_name,
                grpc_streamers=self._grpc_streamers,
            )
        else:
            response = AsyncCatchupSubscription(
                aio_call=unary_stream_call,
                stream_name=stream_name,
                include_checkpoints=include_checkpoints,
                include_caught_up=include_caught_up,
                include_fell_behind=include_fell_behind,
                grpc_streamers=self._grpc_streamers,
            )
            await response.check_confirmation()
        return response

    async def delete(
        self,
        stream_name: str,
        current_version: int | StreamState,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> None:
        delete_req = self._construct_delete_req(stream_name, current_version)

        try:
            delete_resp = await self._stub.Delete(
                delete_req,
                timeout=timeout,
                metadata=self._metadata(metadata, requires_leader=True),
                credentials=credentials,
            )
        except grpc.RpcError as e:
            raise handle_streams_rpc_error(e) from None
        else:
            assert isinstance(delete_resp, streams_pb2.DeleteResp), delete_resp

    async def tombstone(
        self,
        stream_name: str,
        current_version: int | StreamState,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> None:
        tombstone_req = self._construct_tombstone_req(stream_name, current_version)

        try:
            tombstone_resp = await self._stub.Tombstone(
                tombstone_req,
                timeout=timeout,
                metadata=self._metadata(metadata, requires_leader=True),
                credentials=credentials,
            )
        except grpc.RpcError as e:
            raise handle_streams_rpc_error(e) from None
        else:
            assert isinstance(tombstone_resp, streams_pb2.TombstoneResp)


class StreamsService(BaseStreamsService[GrpcStreamers]):
    """
    Encapsulates the 'streams.Streams' gRPC service.
    """

    @overload
    def read(
        self,
        *,
        stream_name: str | None = None,
        stream_position: int | None = None,
        backwards: bool = False,
        resolve_links: bool = False,
        limit: int = sys.maxsize,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> ReadResponse:
        """
        Signature for reading events from a stream.
        """

    @overload
    def read(
        self,
        *,
        stream_name: str | None = None,
        stream_position: int | None = None,
        from_end: bool = False,
        resolve_links: bool = False,
        subscribe: Literal[True],
        include_caught_up: bool = False,
        include_fell_behind: bool = False,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> CatchupSubscription:
        """
        Signature for reading events from a stream with a catch-up subscription.
        """

    @overload
    def read(
        self,
        *,
        commit_position: int | None = None,
        backwards: bool = False,
        resolve_links: bool = False,
        filter_exclude: Sequence[str] = (),
        filter_include: Sequence[str] = (),
        filter_by_stream_name: bool = False,
        limit: int = sys.maxsize,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> ReadResponse:
        """
        Signature for reading all events.
        """

    @overload
    def read(
        self,
        *,
        commit_position: int | None = None,
        from_end: bool = False,
        resolve_links: bool = False,
        filter_exclude: Sequence[str] = (),
        filter_include: Sequence[str] = (),
        filter_by_stream_name: bool = False,
        subscribe: Literal[True],
        include_checkpoints: bool = False,
        window_size: int = DEFAULT_WINDOW_SIZE,
        checkpoint_interval_multiplier: int = DEFAULT_CHECKPOINT_INTERVAL_MULTIPLIER,
        include_caught_up: bool = False,
        include_fell_behind: bool = False,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> CatchupSubscription:
        """
        Signature for reading all events with a catch-up subscription.
        """

    def read(
        self,
        *,
        stream_name: str | None = None,
        stream_position: int | None = None,
        commit_position: int | None = None,
        from_end: bool = False,
        backwards: bool = False,
        resolve_links: bool = False,
        filter_exclude: Sequence[str] = (),
        filter_include: Sequence[str] = (),
        filter_by_stream_name: bool = False,
        limit: int = sys.maxsize,
        subscribe: bool = False,
        include_checkpoints: bool = False,
        window_size: int = DEFAULT_WINDOW_SIZE,
        checkpoint_interval_multiplier: int = DEFAULT_CHECKPOINT_INTERVAL_MULTIPLIER,
        include_caught_up: bool = False,
        include_fell_behind: bool = False,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> ReadResponse | CatchupSubscription:
        """
        Constructs and sends a gRPC 'ReadReq' to the 'Read' rpc.

        Returns a generator which yields RecordedEvent objects.
        """

        # Construct read request.
        read_req = self._construct_read_request(
            stream_name=stream_name,
            stream_position=stream_position,
            commit_position=commit_position,
            from_end=from_end,
            backwards=backwards,
            resolve_links=resolve_links,
            filter_exclude=filter_exclude,
            filter_include=filter_include,
            filter_by_stream_name=filter_by_stream_name,
            limit=limit,
            subscribe=subscribe,
            window_size=window_size,
            checkpoint_interval_multiplier=checkpoint_interval_multiplier,
        )

        # Send the read request, and iterate over the response.
        read_resps = self._stub.Read(
            read_req,
            timeout=timeout,
            metadata=self._metadata(metadata),
            credentials=credentials,
        )
        # assert isinstance(read_resps, _ReadResps)  # a _MultiThreadedRendezvous

        if subscribe is False:
            return ReadResponse(
                read_resps=read_resps,
                stream_name=stream_name,
                grpc_streamers=self._grpc_streamers,
            )
        return CatchupSubscription(
            read_resps=read_resps,
            stream_name=stream_name,
            include_checkpoints=include_checkpoints,
            include_caught_up=include_caught_up,
            include_fell_behind=include_fell_behind,
            grpc_streamers=self._grpc_streamers,
        )

    def append(
        self,
        stream_name: str,
        current_version: int | StreamState,
        events: Iterable[NewEvent],
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> int:
        """
        Constructs and sends a stream of gRPC 'AppendReq' to the 'Append' rpc.

        Returns the commit position of the last appended event.

        This seems to be an atomic operation (either all or none
        """
        try:
            append_reqs = self._generate_append_reqs(
                stream_name=stream_name,
                current_version=current_version,
                events=events,
            )
            append_resp = self._stub.Append(
                append_reqs,
                timeout=timeout,
                metadata=self._metadata(metadata, requires_leader=True),
                credentials=credentials,
            )
        except grpc.RpcError as e:
            raise handle_rpc_error(e) from None
        else:
            assert isinstance(append_resp, streams_pb2.AppendResp)
            # Response 'result' is either 'success' or 'wrong_expected_version'.
            result_oneof = append_resp.WhichOneof("result")
            if result_oneof == "success":
                # Return commit position.
                return append_resp.success.position.commit_position
            assert result_oneof == "wrong_expected_version", result_oneof
            wev = append_resp.wrong_expected_version
            cro_oneof = wev.WhichOneof("current_revision_option")
            if cro_oneof == "current_no_stream":
                msg = f"Stream {stream_name!r} does not exist"
                raise WrongCurrentVersionError(msg)
            assert cro_oneof == "current_revision", cro_oneof
            msg = (
                f"Stream position of last event is"
                f" {wev.current_revision}"
                f" not {current_version}"
            )
            raise WrongCurrentVersionError(msg)
            # if cro_oneof == "current_revision":
            #     msg = f"Current version is {wev.current_revision}"
            #     raise WrongCurrentVersion(msg)
            # else:
            #     assert cro_oneof == "current_no_stream", cro_oneof
            #     msg = f"Stream {stream_name!r} does not exist"
            #     raise WrongCurrentVersion(msg)

    # def batch_append_multiplexed(
    #     self,
    #     futures_queue: BatchAppendFutureQueue,
    #     timeout: Optional[float] = None,
    #     metadata: Optional[Metadata] = None,
    #     credentials: Optional[grpc.CallCredentials] = None,
    # ) -> None:
    #     # Construct batch append requests iterator.
    #     requests = BatchAppendFutureIterator(futures_queue)
    #
    #     # Call the gRPC method.
    #     try:
    #         batch_append_resps = self._stub.BatchAppend(
    #             requests,
    #             timeout=timeout,
    #             metadata=self._metadata(metadata, requires_leader=True),
    #             credentials=credentials,
    #         )
    #
    #         batch_append_resps = BatchAppendResps(
    #             batch_append_resps, self._grpc_streamers
    #         )
    #
    #         for response in batch_append_resps:
    #             # Use the correlation ID to get the future.
    #             assert isinstance(response, streams_pb2.BatchAppendResp)
    #             correlation_id = UUID(response.correlation_id.string)
    #             future = requests.pop_future(correlation_id)
    #
    #             # Convert the result.
    #             stream_name = future.batch_append_request.stream_name
    #             result = self._convert_batch_append_resp(response, stream_name)
    #
    #             # Finish the future.
    #             if isinstance(result, BatchAppendResponse):
    #                 future.set_result(result)
    #             else:
    #                 assert isinstance(result, KurrentDBClientException)
    #                 future.set_exception(result)
    #
    #         else:
    #             # The response stream ended without an RPC error.
    #             for correlation_id in list(
    #                 requests.futures_by_correlation_id
    #             ):  # pragma: no cover
    #                 future = requests.pop_future(correlation_id)
    #                 future.set_exception(
    #                     KurrentDBClientException(
    #                         "Batch append response not received"
    #                     )
    #                 )
    #
    #     except grpc.RpcError as rpc_error:
    #         # The response stream ended with an RPC error.
    #         try:
    #             raise handle_rpc_error(rpc_error) from rpc_error
    #         except CancelledByClient:
    #             while len(requests.futures_by_correlation_id):
    #                 for correlation_id in list(
    #                     requests.futures_by_correlation_id
    #                 ):  # pragma: no cover
    #                     future = requests.pop_future(correlation_id)
    #                     future.set_exception(
    #                         KurrentDBClientException("Cancelled by client")
    #                     )
    #         except GrpcError as grpc_error:
    #             while len(requests.futures_by_correlation_id):
    #                 for correlation_id in list(
    #                     requests.futures_by_correlation_id
    #                 ):  # pragma: no cover
    #                     future = requests.pop_future(correlation_id)
    #                     future.set_exception(grpc_error)

    def batch_append(
        self,
        stream_name: str,
        current_version: int | StreamState,
        events: Iterable[NewEvent],
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> int:
        # Call the gRPC method.
        try:
            req = self._construct_batch_append_req(
                stream_name=stream_name,
                current_version=current_version,
                events=events,
                timeout=timeout,
                correlation_id=uuid4(),
            )
            for response in self._stub.BatchAppend(
                iter([req]),
                timeout=timeout,
                metadata=self._metadata(metadata, requires_leader=True),
                credentials=credentials,
            ):
                assert isinstance(response, streams_pb2.BatchAppendResp)
                return self._convert_batch_append_resp(
                    response, stream_name, current_version
                )
            # no cover: start
            msg = "Batch append response not received"
            raise KurrentDBClientError(msg)
            # no cover: stop

        except grpc.RpcError as e:
            raise handle_rpc_error(e) from None

    def delete(
        self,
        stream_name: str,
        current_version: int | StreamState,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> None:
        delete_req = self._construct_delete_req(stream_name, current_version)

        try:
            delete_resp = self._stub.Delete(
                delete_req,
                timeout=timeout,
                metadata=self._metadata(metadata, requires_leader=True),
                credentials=credentials,
            )
        except grpc.RpcError as e:
            raise handle_streams_rpc_error(e) from None
        else:
            assert isinstance(delete_resp, streams_pb2.DeleteResp)
            # position_option_oneof = delete_resp.WhichOneof("position_option")
            # if position_option_oneof == "position":
            #     return delete_resp.position
            # else:
            #     return delete_resp.no_position

    def tombstone(
        self,
        stream_name: str,
        current_version: int | StreamState,
        timeout: float | None = None,
        metadata: Metadata | None = None,
        credentials: grpc.CallCredentials | None = None,
    ) -> None:
        tombstone_req = self._construct_tombstone_req(stream_name, current_version)

        try:
            tombstone_resp = self._stub.Tombstone(
                tombstone_req,
                timeout=timeout,
                metadata=self._metadata(metadata, requires_leader=True),
                credentials=credentials,
            )
        except grpc.RpcError as e:
            raise handle_streams_rpc_error(e) from None
        else:
            assert isinstance(tombstone_resp, streams_pb2.TombstoneResp)
            # position_option_oneof = tombstone_resp.WhichOneof("position_option")
            # if position_option_oneof == "position":
            #     return tombstone_resp.position
            # else:
            #     return tombstone_resp.no_position


def handle_streams_rpc_error(e: grpc.RpcError) -> KurrentDBClientError:
    if e.code() == grpc.StatusCode.FAILED_PRECONDITION:
        details = e.details() or ""
        if "WrongExpectedVersion" in details:
            if "Actual version: -1" in details:
                return NotFoundError(details)
            return WrongCurrentVersionError(details)
        if "is deleted" in details:
            return StreamIsDeletedError(details)
    return handle_rpc_error(e)
