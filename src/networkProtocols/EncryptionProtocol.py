#Encryption Protocol    LCKJOS003
from src.networkProtocols.BaseProtocol import BaseProtocol
import asyncio
from src.networkProtocols.Encryption import Encryption
#class Encryption Protocol
    #description:
    #     This class handles the encryption protocol required from the chat server via the Encryption class
class EncryptionProtocol(BaseProtocol, asyncio.DatagramProtocol):

    MAX_ATTEMPTS = 6
    
    def __init__(self, encryption : Encryption):
        self.hostname = "csc4026z.link"
        self.port = 51820
        self.transport = None
        self.on_response = None
        self.encryption = encryption
        self.handshake_done = None

    async def start(self, on_response):
        #starts the encrption protocol to async
        self.on_response = on_response
        loop = asyncio.get_running_loop()

        self.handshake_done = loop.create_future()
        await loop.create_datagram_endpoint(lambda: self, remote_addr=(self.hostname, self.port))
        await self._do_handshake()

    def close(self):
        #closes the connection to server
        if self.transport:
            self.transport.close()
            self.transport = None
            print(f"closed transport")

    def connection_made(self, transport):
        #sets the connection transport
        self.transport = transport
        print(f"Socket bound to {self.hostname}:{self.port}")
    
    def send(self, data: bytes):
        #sends message with wireguard header/wrapper to server port
        if self.transport:
            wireguard_wrap = self.encryption.encrypt_transport(data)
            self.transport.sendto(wireguard_wrap, None)
        else:
            raise RuntimeError("cant send; transport not initialised")

    def datagram_received(self, data: bytes, addr: tuple):
        #handles data when it is recieved 
        if self.handshake_done and not self.handshake_done.done():  #Checking to see if handshake is still in progress
            if data[0] == 0x02:
                self.encryption.parse_response(data)
                self.handshake_done.set_result(True) # Unblocking await self.handshake_done
            return

        if self.on_response:
            plain_text = self.encryption.decrypt_transport(data)
            self.on_response(plain_text)

    async def _do_handshake(self):
        #performs the handshake with the server with timeout checking
        packet = self.encryption.build_send_packet()

        for attempt in range(self.MAX_ATTEMPTS):
            try: 
                self.transport.sendto(packet, None)
                await asyncio.wait_for(self.handshake_done, timeout=5.0)
                return
            except asyncio.TimeoutError:
                print("Attempt "+ str(attempt) + " failed due to timeout")
                if (attempt == self.MAX_ATTEMPTS-1):    #last interation
                    raise TimeoutError(f"{packet} timed out")
                self.handshake_done = asyncio.get_running_loop().create_future()    #reset for next iteration
