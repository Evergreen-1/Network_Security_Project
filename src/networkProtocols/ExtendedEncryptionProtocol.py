import asyncio
import EncryptedProtocol
import src.Encryption

class ExtendedEncryptionProtocol(EncryptedProtocol):
    def __init__(self, encryption : src.Encryption.ExtendedEncryption):
        super().__init__(encryption)
        self.port = 51821
        self.handshake_packet = None

    async def start(self, on_response):
        self.on_response = on_response
        loop = asyncio.get_running_loop()

        await loop.create_datagram_endpoint(lambda: self, remote_addr=(self.hostname, self.port))
        await self._do_handshake()

    async def _do_handshake(self):
        loop = asyncio.get_running_loop()
        cookie = None

        while True:
            packet = self.encryption.build_send_packet(cookie)
            self.transport.sendto(packet)

            self.handshake_packet = loop.create_future()

            data = await self.handshake_packet

            if data[0] == 0x02:
                self.encryption.parse_response(data)
                self.handshake_packet = None
                break
            elif data[0] == 0x03:
                cookie = self.encryption.parse_cookie_reply(data)

    def datagram_received(self, data: bytes, addr: tuple):
        if self.handshake_packet and not self.handshake_packet.done():  #Checking to see if handshake is still in progress
            if data[0] in (0x02,0x03):
                self.handshake_packet.set_result(data)
                return

        if self.on_response:
            plain_text = self.encryption.decrypt_transport(data)
            self.on_response(plain_text)
                                                                