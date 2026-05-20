import msgpack # Install with: pip install msgpack
import asyncio
import socket
import random

CleartextAddress = ('csc4026z.link', 51825)

# retry
# pending request handles
# does asyncio.datagram split and combine/buffer the data?

class Channel:
    def __init__(self, channelName, channelDescription):
        self.name = sessionNum
        self.description = channelDescription

class User:
    def __init__(self, channelName, channelDescription):
        self.name = sessionNum
        self.description = channelDescription

class UDPConnection:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.session = None
        self.username = None
        self.running = True
        self.connected = False

    def sendData(self, payload):
        self.sock.send(payload)

    def requestListOfChannels(self, offset = 0):
        if 0==offset:
            self.offset = 0
        else:
            self.offset = offset
        self.sendData(msgpack.packb({'request_type':5, 'session':self.session, 'request_handle': random.randint(0, 2**32 - 1), 'offset': self.offset}))

    def requestChannelInfo(self, channelName):
        self.sendData(msgpack.packb({'request_type':6, 'session':self.session, 'request_handle': random.randint(0, 2**32 - 1), 'channel': channelName}))

    def requestJoinChannel(self, channelName):
        self.sendData(msgpack.packb({'request_type':7, 'session':self.session, 'request_handle': random.randint(0, 2**32 - 1), 'channel': channelName}))

    def requestLeaveChannel(self, channelName):
        self.sendData(msgpack.packb({'request_type':8, 'session':self.session, 'request_handle': random.randint(0, 2**32 - 1), 'channel': channelName}))
    
    def listChannels(self, offset = 0):
        if 0==offset:
            self.offset = 0
        else:
            self.offset = offset
        self.sendData(msgpack.packb({'request_type':5, 'session':self.session, 'request_handle': random.randint(0, 2**32 - 1), 'offset': self.offset}))
    
    async def ping(self):
        print("Starting pinging")
        while self.running:
            try:
                self.sendData(msgpack.packb({'request_type':3, 'session':self.session, 'request_handle': random.randint(0, 2**32 - 1)}))
                print("ping server!")
                await asyncio.sleep(30.0)
            except asyncio.CancelledError:
                print("Asyncio cancelled. Stopped pinging the server.")
                self.running = False
                break
            except Exception as exc:
                print("Error during ping: ", exc)
                await asyncio.sleep(5.0)

    async def recieveLoop(self):
        print("Starting recieving Messages")
        loop = asyncio.get_running_loop()
        while self.running:
            try:
                (data, address) = await loop.sock_recvfrom(self.sock, 4096)
                unpackedData = msgpack.unpackb(data)

                print(unpackedData)
                
                if (unpackedData['response_type'] == 22):
                    self.username = unpackedData['username']
                    self.session = unpackedData['session']
                    print(self.username)
                    print(self.session)
                    asyncio.create_task(self.ping())
                    connected=True
                elif (connected):
                    match unpackedData['response_type']:
                        case 24: # ping response
                            print("ping response recieved")
                        case 26: # list channels response
                            print("Available channels: ", unpackedData['channels'])
                            count = len(unpackedData['channels'])
                            if unpackedData['next_page']:
                                self.listChannels(self.offset + count)
                        case 27: # channel info
                            print("Found channel info for channel: " + unpackedData['channel'])
                            print("Desc: " + unpackedData['description'])
                            print("Members: " + unpackedData['members'])
                        case 28: # channel join
                            print("User: " + unpackedData['username'] + " has joined the channel("+unpackedData['channel']+")")
                            print("Channel desc: "+ unpackedData['description'])
                            if (unpackedData['username'] != self.username):
                                print("another user joined channel!")
                            
                        case _:
                            print("Unregistered response_type: ", unpackedData['response_type'])
                # then we get session id
                # and then asyncio.create_task(ping())
                
            except asyncio.CancelledError:
                print("Asyncio cancelled. Stopped pinging the server.")
                self.running = False
                break
            except Exception as exc:
                print("Error during receive: ", exc)
                await asyncio.sleep(5.0)
    
    async def ConnectCleartext(self):
        self.sock.connect(CleartextAddress)
        asyncio.create_task(self.recieveLoop())
        self.sendData(msgpack.packb({'request_type':1, 'request_handle': random.randint(0, 2**32 - 1)}))

    def ConnectEncrypted(self):
        print("Connected to encrypted chat!")

async def get_user_input_async(prompt):
    loop = asyncio.get_running_loop()
    # Runs standard blocking input() safely on a background thread
    return await loop.run_in_executor(None, input, prompt)

if __name__ == "__main__":
    con = UDPConnection()
    # Simulating your active async UI environment boot sequence
    async def main_runner():
        await con.ConnectCleartext()

        while con.running:
            text = await get_user_input_async("enter:\n0 for quit\n1 for view channels\n2 for view users\n")
            print("user entered: ", text)
            if (text == '0'):
                break
            elif (text == '1'):
                con.listChannels();
            elif (text == '2'):
                con.listUsers();

    asyncio.run(main_runner())
