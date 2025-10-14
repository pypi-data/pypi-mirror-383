import grpc
from typing import Any, List, Optional
from enum import Enum
from dataclasses import is_dataclass, asdict as dc_asdict
# API imports
from ..base import Action
from ..datatypes.common import Response
from google.protobuf.timestamp_pb2 import Timestamp
import logging
logger = logging.getLogger(__name__)

def now_ts() -> Timestamp:
    """Get the current time as a Google Protobuf Timestamp.
    
    Returns the current time as a Google Protobuf Timestamp object.
    This is useful for setting the timestamp field inside a Request
    object.

    Returns:
        Timestamp: current timestamp as a Google Protobuf Timestamp object.
    """
    ts = Timestamp()
    ts.GetCurrentTime()
    return ts

def payload_from_action(action: Action) -> dict:
    """Get the payload of an Action object as JSON.

    Returns a JSON-ified version of the input Action object. This
    is usually used to translate from the Python API into the Protobuf
    API for serialization over the wire.

    Args:
        action (Action): input Action to be JSON serialized.

    Returns:
        dict: JSON serialized version of the input action.
    """
    data = action.model_dump(exclude_none=True, by_alias=True, mode = "json")  # v2
    return data

def error_to_api_response(error: grpc.aio.AioRpcError) -> Response:
    """Get the corresponding Python API Response for an error code.

    Returns a Python API Response for a corresponding gRPC error code.
    Allows transformation of gRPC exceptions into a unified Response.

    Args:
        error (grpc.aio.AioRpcError): input gRPC Exception object.

    Returns:
        Response: Python API Response object.
    """
    ts = now_ts()
    # Note: gRPC error codes start from 0, API Response codes start from 2
    return Response(status=error.code().value[0] + 2, response_string=error.details(), timestamp=ts)

async def run_unary(method_coro: Any, request_pb: Any, metadata: Optional[list]=[('identity', 'internal')], timeout: Optional[int]=None) -> Response:
    """Runs a unary gRPC method and returns a Python API Response.

    Runs a unary gRPC method, gets the response (or error), and translates
    it into a Python API Response.

    Args:
        method_coro (Any): an awaitable stub coroutine <stub>.<method> e.g.
            ControlStub.Connect.
        request_pb (Any): Protobuf object input for the method coroutine.
        metadata (`Optional[list]`, default: `[('identity', 'internal')]`): 
            metadata object for gRPC. The metadata must include an `identity` 
            parameter to access kernel services. An `identity` set to 
            `internal` signals to the kernel that the RPC request originates
            from an onboard client.
        timeout (`Optional[int]`, default: `None`): timeout for the RPC request,
            `None` indicates no timeout.

    See Also:
        - [Law Documentation](primitives/control#connect-objects): full documentation of RPC identities and how
            they are interpreted by the kernel.
    """
    ts = now_ts()
    request_pb.request.timestamp.CopyFrom(ts)
    try:
        resp_pb = await method_coro(request_pb, metadata=metadata, timeout=timeout)
        return resp_pb
    except grpc.aio.AioRpcError as e:
        return error_to_api_response(e)

async def run_streaming(method_coro: Any, request_pb: Any, metadata: Optional[list]=[('identity', 'internal')], timeout: Optional[int]=None) -> Response:
    """Runs a streaming gRPC method and returns a Python API Response.

    Runs a streaming gRPC method, gets the response (or error), and translates
    it into a Python API Response. This method will only return the _last_
    response it receives from the RPC.

    Args:
        method_coro (Any): an async generator stub coroutine <stub>.<method> e.g.
            ControlStub.TakeOff.
        request_pb (Any): Protobuf object input for the method coroutine.
        metadata (`Optional[list]`, default: `[('identity', 'internal')]`): 
            metadata object for gRPC. The metadata must include an `identity` 
            parameter to access kernel services. An `identity` set to 
            `internal` signals to the kernel that the RPC request originates
            from an onboard client.
        timeout (`Optional[int]`, default: `None`): timeout for the RPC request,
            `None` indicates no timeout. It is generally not recommended to add
            a timeout to a streaming method, since most have non-deterministic
            time of completion.

    See Also:
        - [Law Documentation](primitives/control#connect-objects): full documentation of RPC identities and how
            they are interpreted by the kernel.
    """
    ts = now_ts()
    request_pb.request.timestamp.CopyFrom(ts)
    call = method_coro(request_pb, metadata=metadata, timeout=timeout)
    last = None
    try:
        async for msg in call:
            last = msg  # Guaranteed at least one response
        logger.info(f"Streaming response received: {last}")
        return last
    except grpc.aio.AioRpcError as e:
        return error_to_api_response(e)
