# KRNRUA001

import asyncio
import msgpack
import random

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
            raise RuntimeError("unpack was unsuccessful")

    async def send(self, outgoing_data: dict) -> dict:
        if self.session:
            outgoing_data["session"] = self.session
        elif outgoing_data["request_type"] is not 1:
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

        response_type = response.get("response_type")
        response_handle = response.get("response_handle")

        if response_handle is not None and response_handle in self.pending: # reply
            target_future = self.pending[response_handle]
            if not target_future.done():
                if response_type is 20 or "error" in response:
                    target_future.set_exception(RuntimeError(response.get("error")))
                else:
                    target_future.set_result(response)
        else:   # unsolicited response
            event = self.make_event(response) # TODO: MAYBE ADD TRY CATCH??
            if event:
                 self.event_queue.put_nowait(event)

    def make_event(self, response: dict):
         pass