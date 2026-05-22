import asyncio
import socket
import BaseProtocol
import src.Encryption

class EncryptionProtocol(BaseProtocol, asyncio.DatagramProtocol):
    
    def __init__(self, encryption : src.Encryption.Encryption):
        self.hostname = "csc4026z.link"
        self.port = 51820
        self.transport = None
        self.on_response = None
        self.encryption = encryption
        self.handshake_done = None

    async def start(self, on_response):
        self.on_response = on_response
        loop = asyncio.get_running_loop()

        self.handshake_done = loop.create_future()
        await loop.create_datagram_endpoint(lambda: self, remote_addr=(self.hostname, self.port))
        await self._do_handshake()

    def connection_made(self, transport):
        self.transport = transport
        print(f"Socket bound to {self.hostname}:{self.port}")
    
    def send(self, data: bytes):
        if self.transport:
            wireguard_wrap = self.encryption.encrypt_transport(data)
            self.transport.sendto(wireguard_wrap)
        else:
            raise RuntimeError("cant send; transport not initialised")

    def datagram_received(self, data: bytes, addr: tuple):
        if self.handshake_done and not self.handshake_done.done():  #Checking to see if handshake is still in progress
            if data[0] == 0x02:
                self.encryption.parse_response(data)
                self.handshake_done.set_result(True) # Unblocking await self.handshake_done
            return

        if self.on_response:
            plain_text = self.encryption.decrypt_transport(data)
            self.on_response(plain_text)

    async def _do_handshake(self):
        packet = self.encryption.build_send_packet()
        self.transport.sendto(packet)

        await self.handshake_done