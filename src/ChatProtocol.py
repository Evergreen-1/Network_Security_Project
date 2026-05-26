# KRNRUA001
# class that creates the mechanisms by which requests and
# responses are created/sent/received/handled, along with
# incorporating msgpack packing/unpacking

import asyncio
import msgpack
import random
from src.eventDataclasses import (
    UserMessageEvent,
    ChannelMessageEvent,
    ChannelJoinEvent,
    ChannelLeaveEvent,
    UsernameChangeEvent,
    ServerMessageEvent,
    ServerShutdownEvent
)
from src.networkProtocols import BaseProtocol
from src.OpCode import OpCode

class ChatProtocol:

    # constructor
    def __init__(self, transport_protocol):
        self.transport_protocol = transport_protocol
        self.session = None
        self.pending = {}
        self.event_queue = asyncio.Queue()

    # property used higher up to determine whether protocol being used is cleartext
    @property
    def is_cleartext(self) -> bool:
        return getattr(self.transport_protocol, "is_cleartext", False)

    # packs with msgpack
    def pack(self, outgoing_data: dict) -> bytes:
        return msgpack.packb(outgoing_data)

    #unpacks with msgpack
    def unpack(self, incoming_data: bytes) -> dict:
        try:
            return msgpack.unpackb(incoming_data, raw=False)
        except msgpack.UnpackException:
            raise RuntimeError("unpack was unsuccessful") from None

    # calls on the relevant protocol start method for setting up
    async def start(self):
        await self.transport_protocol.start(self.on_response)

    # builds a request and uses the relevant protocol's send to transport
    async def send(self, outgoing_data: dict) -> dict:
        # add session info
        if self.session:
            outgoing_data["session"] = self.session
        elif outgoing_data["request_type"] != OpCode.CONNECT:
            raise RuntimeError("not in a session")
        
        # add request handle
        while True:
            request_handle = random.randint(0, 2**32 - 1)
            if request_handle not in self.pending:
                break

        outgoing_data["request_handle"] = request_handle

        # create future for expected response and send
        future = asyncio.get_running_loop().create_future()
        self.pending[request_handle] = future
        self.transport_protocol.send(self.pack(outgoing_data))

        # handle future
        try:
             return await asyncio.wait_for(future, timeout=5.0)
        except asyncio.TimeoutError:
             raise TimeoutError(f"{request_handle} timed out")
        finally:
             self.pending.pop(request_handle, None)

    # calls on the relevant protocol close method for shutting down
    def close(self):
        self.transport_protocol.close()

    # handles received responses, called when a datagram is received
    def on_response(self, data: bytes):
        # get response
        try:
            response = self.unpack(data)
        except RuntimeError:
            print("dropping packet")
            return
        
        # retrieve basic response info after required checks
        if not isinstance(response, dict):
            print("response isnt a dictionary")
            return
        
        if "response_type" not in response or "response_handle" not in response:
            print("response doesnt have expected fields for some reason")
            return

        response_type = response.get("response_type")
        response_handle = response.get("response_handle")

        # expected reply - sort out future
        if response_handle is not None and response_handle in self.pending:
            target_future = self.pending[response_handle]
            if not target_future.done():
                if response_type == OpCode.ERROR or "error" in response:
                    target_future.set_exception(RuntimeError(response.get("error") or "error"))
                else:
                    target_future.set_result(response)
                    
        # unsolicited response - create event dataclass
        else:
            try:
                event = self.make_event(response_type, response)
                if event:
                    self.event_queue.put_nowait(event)
            except Exception as e:
                print(f"issue with unsolicited response: {e}")

    # creates the relevant event dataclass
    def make_event(self, response_type, response: dict):
        try:
            match response_type:
                case OpCode.USER_MESSAGE_RESP:
                    return UserMessageEvent(
                        username=response.get("from_username", "unknown"),
                        message=response.get("message", "")
                    )
                case OpCode.CHANNEL_MESSAGE_RESP:
                    return ChannelMessageEvent(
                        channel=response.get("channel", "unknown"),
                        username=response.get("username", "unknown"),
                        message=response.get("message", "")
                    )
                case OpCode.CHANNEL_JOIN_RESP:
                    return ChannelJoinEvent(
                        channel=response.get("channel", "unknown"),
                        username=response.get("username", "unknown"),
                        description=response.get("description", "")
                    )
                case OpCode.CHANNEL_LEAVE_RESP:
                    return ChannelLeaveEvent(
                        channel=response.get("channel", "unknown"),
                        username=response.get("username", "unknown")
                    )
                case OpCode.SET_USERNAME_RESP:
                    return UsernameChangeEvent(
                        old_username=response.get("old_username", "unknown"),
                        new_username=response.get("new_username", "unknown")
                    )
                case OpCode.SERVER_MESSAGE:
                    return ServerMessageEvent(
                        message=response.get("message", "")
                    )
                case OpCode.SERVER_SHUTDOWN:
                    return ServerShutdownEvent(
                        message=response.get("message", "server is shutting down.")
                    )
                case _:
                    return None
        except KeyError as e:
            print(f"a key is missing from response: {e}")
            return None