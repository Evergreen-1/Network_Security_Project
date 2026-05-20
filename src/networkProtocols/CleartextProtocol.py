# KRNRUA001

import asyncio
import socket

class CleartextProtocol(BaseProtocol, asyncio.DatagramProtocol):

    def __init__(self):
        super().__init__()
        self.hostname = "csc4026z.link"
        self.port = 51825
        self.transport = None
        self.on_response = None

    async def start(self, on_response):
        self.on_response = on_response
        loop = asyncio.get_running_loop()

        await loop.create_datagram_endpoint(lambda: self, remote_addr=(self.hostname, self.port))

        # self.sock = asyncio.get_event_loop().create_datagram_endpoint(asyncio.DatagramProtocol, remote_addr=(self.hostname, self.port))

        # self.receive_task = asyncio.create_task(self.receive)

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

    # def __init__(self):
    #     self.hostname = "csc4026z.link"
    #     self.port = 51825
    #     self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     self.sock.settimeout(2.0)
    #     self._receive = None

    # def start(self, on_receive):
    #     self._receive = on_receive

    # def send(self, data: bytes):
    #     max_retries = 3
    #     num_attempts = 0

    #     while num_attempts < max_retries:
    #         try:
    #             print(f"sending request: {num_attempts+1}/{max_retries}")
    #             self.sock.sendto(data, (self.hostname, self.port))

    #             response_data, server_address = self.sock.recvfrom(2048)
    #             print(f"response received from {server_address}")

    #             if self._receive:
    #                 self._receive(response_data)

    #             return
        
    #         except socket.timeout:
    #             num_attempts += 1
    #             print("request timed out on attempt {num_attempts}")
    #             if num_attempts >= max_retries:
    #                 print("max retries attempted")

    #         except socket.gaierror:
    #             print("dns resolution failed")
    #             break

    # def close(self):
    #     self.sock.close()