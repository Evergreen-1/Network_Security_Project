import asyncio
import EncryptedProtocol

class ExtendedEncryptionProtocol(EncryptedProtocol):
    def __init__(self, encryption : ExtendedEncryption):
        super().__init__(encryption)
        self.port = 51821

    async def _do_handshake(self):
        # 1. Send initial packet (mac2 = 0)
        # 2. Receive type 0x03 cookie reply
        # 3. Parse cookie via self.encryption.parse_cookie_reply()
        # 4. Resend with mac2 calculated from cookie
        # 5. Receive type 0x02 response, call self.encryption.parse_response()
        pass