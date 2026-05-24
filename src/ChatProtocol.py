# KRNRUA001

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

# from enum import IntEnum

# OpCode = IntEnum("OpCode", [
#     ("CONNECT", 1),
#     ("DISCONNECT", 2),
#     ("ERROR", 20),
#     ("USER_MESSAGE", 33),
#     ("CHANNEL_MESSAGE", 30),
#     ("CHANNEL_JOIN", 28),
#     ("CHANNEL_LEAVE", 29),
#     ("USERNAME_CHANGE", 34),
#     ("SERVER_MESSAGE", 36),
#     ("SERVER_SHUTDOWN", 37)
# ])

class ChatProtocol:

    def __init__(self, transport_protocol):
        self.transport_protocol = transport_protocol
        self.session = None
        self.pending = {}
        self.event_queue = asyncio.Queue()

    @property
    def is_cleartext(self) -> bool:
        return getattr(self.transport_protocol, "is_cleartext", False)

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
        elif outgoing_data["request_type"] != OpCode.CONNECT:
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

    def close(self):
        self.transport_protocol.close()

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
                if response_type == OpCode.ERROR or "error" in response:
                    target_future.set_exception(RuntimeError(response.get("error") or "error"))
                else:
                    target_future.set_result(response)
        else:   # unsolicited response
            try:
                event = self.make_event(response_type, response)
                if event:
                    self.event_queue.put_nowait(event) # could add try catch to prevent queue explosion
            except Exception as e:
                print(f"issue with unsolicited response: {e}")

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
        
                # match response_type:
        #     case OpCode.USER_MESSAGE_RESP:    # User Message
        #         return UserMessageEvent(
        #             username=response["from_username"],
        #             message=response["message"]
        #         )
        #     case OpCode.CHANNEL_MESSAGE_RESP:    # Channel Message
        #         return ChannelMessageEvent(
        #             channel=response["channel"],
        #             username=response["username"],
        #             message=response["message"]
        #         )
        #     case OpCode.CHANNEL_JOIN_RESP:    # Channel Join
        #         return ChannelJoinEvent(
        #             channel=response["channel"],
        #             username=response["username"],
        #             description=response["description"]
        #         )
        #     case OpCode.CHANNEL_LEAVE_RESP:    # Channel Leave
        #         return ChannelLeaveEvent(
        #             channel=response["channel"],
        #             username=response["username"]
        #         )
        #     case OpCode.SET_USERNAME_RESP:    # Username Change
        #         return UsernameChangeEvent(
        #             old_username=response["old_username"],
        #             new_username=response["new_username"]
        #         )
        #     case OpCode.SERVER_MESSAGE:    # Server Message
        #         return ServerMessageEvent(
        #             message=response["message"]
        #         )
        #     case OpCode.SERVER_SHUTDOWN:    # Server Shutdown
        #         return ServerShutdownEvent(
        #             message=response["message"]
        #         )
        #     case _:
        #         return None
            
            
        
