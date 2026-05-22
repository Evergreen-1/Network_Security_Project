# KRNRUA001

import asyncio
import msgpack
import random
from eventDataclasses import (
    UserMessageEvent,
    ChannelMessageEvent,
    ChannelJoinEvent,
    ChannelLeaveEvent,
    UsernameChangeEvent,
    ServerMessageEvent,
    ServerShutdownEvent
)
from networkProtocols import BaseProtocol

class ChatProtocol:

    def __init__(self, transport_protocol):
        self.transport_protocol = transport_protocol
        self.session = None
        self.pending = {}
        self.event_queue = asyncio.Queue()

    def pack(self, outgoing_data: dict) -> bytes:
        return msgpack.packb(outgoing_data)
    
    def unpack(self, incoming_data: bytes) -> dict:
        try:
            return msgpack.unpackb(incoming_data, raw=False)
        except msgpack.UnpackException:
            raise RuntimeError("unpack was unsuccessful") from None
        
    async def start(self):
        await self.transport_protocol.start(self.on_response)

    async def send(self, outgoing_data: dict) -> dict:
        if self.session:
            outgoing_data["session"] = self.session
        elif outgoing_data["request_type"] != 1:
            raise RuntimeError("not in a session")
        
        while True:
            request_handle = random.randint(0, 2**32 - 1)
            if request_handle not in self.pending:
                break

        outgoing_data["request_handle"] = request_handle

        future = asyncio.get_running_loop().create_future()
        self.pending[request_handle] = future
        self.transport_protocol.send(self.pack(outgoing_data))

        try:
             return await asyncio.wait_for(future, timeout=5.0)
        except asyncio.TimeoutError:
             raise TimeoutError(f"{request_handle} timed out")
        finally:
             self.pending.pop(request_handle, None)

    def on_response(self, data: bytes):
        try:
            response = self.unpack(data)
        except RuntimeError:
            print("dropping packet")
            return
        
        if not isinstance(response, dict):
            print("response isnt a dictionary")
            return
        
        if "response_type" not in response or "response_handle" not in response:
            print("response doesnt have expected fields for some reason")
            return

        response_type = response.get("response_type")
        response_handle = response.get("response_handle")

        if response_handle is not None and response_handle in self.pending: # reply
            target_future = self.pending[response_handle]
            if not target_future.done():
                if response_type == 20 or "error" in response:
                    target_future.set_exception(RuntimeError(response.get("error")))
                else:
                    target_future.set_result(response)
        else:   # unsolicited response
            try:
                event = self.make_event(response_type, response)
                if event:
                    self.event_queue.put_nowait(event)
            except Exception as e:
                print(f"issue with unsolicited response: {e}")

    def make_event(self, response_type, response: dict):
        match response_type:
            case 33:    # User Message
                return UserMessageEvent(
                    username=response["from_username"],
                    message=response["message"]
                )
            case 30:    # Channel Message
                return ChannelMessageEvent(
                    channel=response["channel"],
                    username=response["username"],
                    message=response["message"]
                )
            case 28:    # Channel Join
                return ChannelJoinEvent(
                    channel=response["channel"],
                    username=response["username"],
                    description=response["description"]
                )
            case 29:    # Channel Leave
                return ChannelLeaveEvent(
                    channel=response["channel"],
                    username=response["username"]
                )
            case 34:    # Username Change
                return UsernameChangeEvent(
                    old_username=response["old_username"],
                    new_username=response["new_username"]
                )
            case 36:    # Server Message
                return ServerMessageEvent(
                    message=response["message"]
                )
            case 37:    # Server Shutdown
                return ServerShutdownEvent(
                    message=response["message"]
                )
            case _:
                return None