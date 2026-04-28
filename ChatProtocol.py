import msgpack # Install with: pip install msgpack
import socket
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(('csc4026z.link', 51825))
sock.send(msgpack.packb({'session': 1, 'request_type':3, 'request_handle': random.randint(0, 2**32 - 1)}))
data, addr = sock.recvfrom(4096)
print(msgpack.unpackb(data))

# This will return an error saying "Session not found", because you're not logged in yet. That confirms the server is active.