import msgpack # Install with: pip install msgpack
import socket
import random

class UDPConnection:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def ConnectCleartext(self):
        self.sock.connect(('csc4026z.link', 51825))
        self.sock.send(msgpack.packb({'request_type':1, 'request_handle': random.randint(0, 2**32 - 1)}))
        data, addr = self.sock.recvfrom(4096)
        print(msgpack.unpackb(data))

    def ConnectEncrypted(self):
        print("Connected to encrypted chat!")

con = UDPConnection()
con.ConnectCleartext()
# make a class to manage udp commands.