# KRNRUA001
# concrete protocol implementing BaseProtocol
# for cleartext communication

from src.networkProtocols.BaseProtocol import BaseProtocol
import asyncio

class CleartextProtocol(BaseProtocol, asyncio.DatagramProtocol):

    # constructor
    def __init__(self):
        super().__init__()
        self.hostname = "csc4026z.link"
        self.port = 51825
        self.transport = None
        self.on_response = None
        self.is_cleartext = True

    # sets up everything that will be required to send and receive messages
    async def start(self, on_response):
        if self.transport is not None:
            raise RuntimeError("already started")
        self.on_response = on_response
        loop = asyncio.get_running_loop()
        try:
            await loop.create_datagram_endpoint(
                lambda: self,
                remote_addr=(self.hostname, self.port)
            )
        except Exception as e:
            raise ConnectionError(f"DNS went wrong 0_0: {e}") from None

    # transports pure bytes
    def send(self, data: bytes):
        if self.transport:
            self.transport.sendto(data, None)
        else:
            raise RuntimeError("cant send; transport not initialised")

    # shuts everything down that was set up
    def close(self):
        if self.transport:
            self.transport.close()
            self.transport = None
            print(f"closed transport")

    # overwritten asyncio method
    def connection_made(self, transport):
        self.transport = transport
        print(f"socket bound to {self.hostname}:{self.port}")

    # overwritten asyncio method
    def datagram_received(self, data: bytes, addr: tuple):
        if self.on_response:
            try:
                self.on_response(data)
            except Exception as e:
                print(f"exception when datagram received: {e}")

    # overwritten asyncio method
    def error_received(self, exception):
        print(f"error: {exception}")
        if self.transport:
            self.transport.close()
