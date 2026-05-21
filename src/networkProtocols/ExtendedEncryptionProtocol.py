import asyncio
import EncryptedProtocol

class ExtendedEncryptionProtocol(EncryptedProtocol):
    def __init__(self, encryption : ExtendedEncryption):
        super().__init__(encryption)
        self.port = 51821

    async def _do_handshake(self):
        loop = asyncio.get_running_loop()
        cookie = None
        while True:                                                           
            packet = self.encryption.build_send_packet(cookie)
            self.transport.sendto(packet)
                                                                
            data, _ = await loop.sock_recvfrom(self.sock, 4096)
            
            if data[0] == 0x02:                                 
                self.encryption.parse_response(data)
            elif data[0] == 0x03:                               
                cookie = self.encryption.parse_cookie_reply(data)
                                                                