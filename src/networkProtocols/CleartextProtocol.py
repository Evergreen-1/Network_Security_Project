# KRNRUA001

from .BaseProtocol import BaseProtocol
import asyncio

class CleartextProtocol(BaseProtocol, asyncio.DatagramProtocol):

    def __init__(self):
        super().__init__()
        self.hostname = "csc4026z.link"
        self.port = 51825
        self.transport = None
        self.on_response = None
        self.is_cleartext = True

    async def start(self, on_response):
        self.on_response = on_response
        loop = asyncio.get_running_loop()
        try:
            await loop.create_datagram_endpoint(lambda: self, remote_addr=(self.hostname, self.port))
        except Exception as e:
            raise ConnectionError(f"DNS went wrong 0_0: {e}") from None

    def send(self, data: bytes):
        if self.transport:
            self.transport.send(data)
        else:
            raise RuntimeError("cant send; transport not initialised")

    def close(self):
        if self.transport:
            self.transport.close()
            print(f"closed transport")

    def connection_made(self, transport):
        self.transport = transport
        print(f"socket bound to {self.hostname}:{self.port}")

    def datagram_received(self, data: bytes, addr: tuple):
        if self.on_response:
            self.on_response(data)

    def error_received(self, exception):
        print(f"error: {exception}")
        if self.transport:
            self.transport.close()