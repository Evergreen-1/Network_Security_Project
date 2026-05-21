import asyncio
import socket
import BaseProtocol

class EncryptionProtocol(BaseProtocol, asyncio.DatagramProtocol):
    
    def __init__(self, encryption : Encryption):
        self.hostname = "csc4026z.link"
        self.port = 51820
        self.transport = None
        self.on_response = None
        self.encryption = encryption

    async def start(self, on_response):
        self.on_response = on_response
        loop = asyncio.get_running_loop()
        await self._do_handshake()
        await loop.create_datagram_endpoint(lambda: self, remote_addr=(self.hostname, self.port))

    def send(self, data: bytes):
        if self.transport:
            wireguard_wrap = self.encryption.encrypt_transport(data)
            self.transport.sendto(wireguard_wrap)
        else:
            raise RuntimeError("cant send; transport not initialised")

    def datagram_received(self, data: bytes, addr: tuple):
        if self.on_response:
            plain_text = self.encryption.decrypt_transport(data)
            self.on_response(plain_text)

    async def _do_handshake(self):
        loop = asyncio.get_running_loop()

        packet = self.encryption.build_send_packet()
        self.transport.sendto(packet)
        # Wait for type 0x02 response
        while True:
            data, _ = await loop.sock_recvfrom(self.sock, 4096)
            if data[0] == 0x02:
                break
        self.encryption.parse_response(data)