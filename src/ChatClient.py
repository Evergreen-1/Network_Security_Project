# KRNRUA001
# class that implements all functions that are to be called by UI
# along with storing state and implementing important background tasks

from src.ChatProtocol import ChatProtocol
from src.eventDataclasses import UsernameChangeEvent, ServerShutdownEvent
import asyncio
from src.OpCode import OpCode

class ChatClient:

    #constructor
    def __init__(self, chat_protocol: ChatProtocol):
        self.chat_protocol = chat_protocol
        self.session = None
        self.username = None
        self.joined_channels = set()
        self.on_event = None
        self.ping_task = None
        self.event_task = None

    # connects to chat server
    async def connect(self):
        # calls lower level start, sends request, and stores response
        await self.chat_protocol.start()
        response = await self.chat_protocol.send({
            "request_type": OpCode.CONNECT
            })

        # saves given session value
        self.session = response.get("session", None)
        if not self.session:
            raise RuntimeError("server did not return a session")
        
        # passes on session value and stores given username
        self.chat_protocol.session = self.session
        self.username = response.get("username")

        # creates ping and dispatch events background tasks
        self.ping_task = asyncio.create_task(self._ping())
        self.event_task = asyncio.create_task(self._dispatch_events())

        # returns the server message
        return response.get("message")

    # continuously pings chat server
    async def _ping(self):
        # continuously runs
        while True:
            try:
                # send request every 30 seconds
                await asyncio.sleep(30)
                await self.chat_protocol.send({
                    "request_type": OpCode.PING
                    })
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"ping failed: {e}")

    # disconnects from chat server
    async def disconnect(self):
        # check not already disconnected
        if not self.session:
            return "already disconnected"

        # cancel ping task safely
        if self.ping_task and not self.ping_task.done():
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass

        # cancel event task safely
        if self.event_task and not self.event_task.done():
            self.event_task.cancel()
            try:
                await self.event_task
            except asyncio.CancelledError:
                pass
        
        # send request and change saved state as required
        try:
            response = await asyncio.shield(self.chat_protocol.send({
                "request_type": OpCode.DISCONNECT
                }))
            
            # return server message
            return response.get("message") or "disconnected"

        except Exception as e:
            return f"failed to deliver disconnect message: {e}"
        finally:
            self.session = None
            self.chat_protocol.session = None
            self.username = None
            self.joined_channels = set()
            self.chat_protocol.close()

    # creates a channel
    async def create_channel(self, channel, description):
        # validate channel name
        channel = channel.strip() if channel else ""
        if not channel:
            raise ValueError("channel name cant be empty")
        if len(channel) > 20:
            raise ValueError("channel name cant be longer than 20 characters")
        
        # validate description
        description = description.strip() if description else ""
        if not description:
            raise ValueError("description cant be empty")
        if len(description) > 100:
            raise ValueError("description cant be longer than 100 characters")
        
        # send request and save joined channel
        response = await self.chat_protocol.send({
            "request_type": OpCode.CHANNEL_CREATE,
            "channel": channel,
            "description": description
        })
        self.joined_channels.add(channel)

        # return response dictionary
        return response

    # returns a list of all channels
    async def list_channels(self):
        # initialise required variables
        channels = []
        offset = 0
        max_pages = 100
        page_count = 0

        # go through pages as long as there is another page and havent reached max
        while page_count < max_pages:
            # create request (only include offset if there is one)
            request = {"request_type": OpCode.CHANNEL_LIST}
            if offset > 0:
                request["offset"] = offset
            response = await self.chat_protocol.send(request)

            # safely store list of channels
            received_channels = response.get("channels", [])
            if received_channels:
                channels.extend(received_channels)

            # check for there being a next page
            if not response.get("next_page"):
                break

            # increment required variables
            offset += 10
            page_count += 1
        
        # return list of channels
        return channels

    # returns the info of a specified channel
    async def channel_info(self, channel):
        # validate channel name
        channel = channel.strip() if channel else ""
        if not channel:
            raise ValueError("channel name cant be empty")
        if len(channel) > 20:
            raise ValueError("channel name cant be longer than 20 characters")
        
        # send request and safely handle response
        response = await self.chat_protocol.send({
            "request_type": OpCode.CHANNEL_INFO,
            "channel": channel
        })
        if "members" not in response:
            response["members"] = []

        # return response dictionary
        return response

    # joins a channel
    async def join_channel(self, channel):
        # validate channel name
        channel = channel.strip() if channel else ""
        if not channel:
            raise ValueError("channel name cant be empty")
        if len(channel) > 20:
            raise ValueError("channel name cant be longer than 20 characters")
        
        # send request and save joined channel
        response = await self.chat_protocol.send({
            "request_type": OpCode.CHANNEL_JOIN,
            "channel": channel
        })
        self.joined_channels.add(channel)

        # return response dictionary
        return response

    # leaves a channel
    async def leave_channel(self, channel):
        # validate channel name
        channel = channel.strip() if channel else ""
        if not channel:
            raise ValueError("channel name cant be empty")
        if len(channel) > 20:
            raise ValueError("channel name cant be longer than 20 characters")
        
        # send request and save left channel
        response = await self.chat_protocol.send({
            "request_type": OpCode.CHANNEL_LEAVE,
            "channel": channel
        })
        self.joined_channels.discard(channel)

        # return response dictionary
        return response

    # sends a message on a channel
    async def message_channel(self, channel, message):
        # validate channel name
        channel = channel.strip() if channel else ""
        if not channel:
            raise ValueError("channel name cant be empty")
        if len(channel) > 20:
            raise ValueError("channel name cant be longer than 20 characters")
        
        # validate message
        if not message or message.isspace():
            raise ValueError("message cant be empty or just whitespace")
        if len(message) > 500:
            raise ValueError("message cant be longer than 500 characters")
        
        # send request
        response = await self.chat_protocol.send({
            "request_type": OpCode.CHANNEL_MESSAGE,
            "channel": channel,
            "message": message
        })

        # return response dictionary
        return response

    # changes username
    async def set_username(self, username):
        # validate username
        username = username.strip() if username else ""
        if not username:
            raise ValueError("username cant be empty")
        if self.chat_protocol.is_cleartext and not username.startswith("clear-"):
            raise ValueError("cleartext usernames have to start with 'clear-'")
        if ':' in username:
            raise ValueError("cant have colon in username")
        if len(username) > 20:
            raise ValueError("username cant be longer than 20 characters")
        
        # send request and save username
        response = await self.chat_protocol.send({
            "request_type": OpCode.SET_USERNAME,
            "username": username
        })
        self.username = response.get("new_username") or self.username

        # return username
        return self.username

    # returns a list of users (optionally within a channel)
    async def list_users(self, channel=None):
        # validate channel name if one is given
        if channel:
            channel = channel.strip() if channel else ""
            if len(channel) > 20:
                raise ValueError("channel name cant be longer than 20 characters")

        # initialise required variables
        users = []
        offset = 0
        max_pages = 50
        page_count = 0

        # go through pages as long as there is another page and havent reached max
        while page_count < max_pages:
            # create request (only include channel and offset if there is one)
            request = {"request_type": OpCode.USER_LIST}
            if channel:
                request["channel"] = channel
            if offset > 0:
                request["offset"] = offset
            response = await self.chat_protocol.send(request)

            # safely save users
            received_users = response.get("users", [])
            if received_users:
                users.extend(received_users)

            # check for if there is a next page
            if not response.get("next_page"):
                break

            # increment required variables
            offset += 20
            page_count += 1
        
        # return list of users
        return users

    # sends a message to a user
    async def message_user(self, username, message):
        # validate username
        username = username.strip() if username else ""
        if not username:
            raise ValueError("username cant be empty")
        if self.chat_protocol.is_cleartext and not (username.startswith("clear-") or username.startswith("cleartext_user_")):
            raise ValueError("cleartext usernames have to start with 'clear-'")
        if ':' in username:
            raise ValueError("cant have colon in username")
        if len(username) > 23:
            raise ValueError("username cant be longer than 20 characters")
        
        # validate message
        if not message or message.isspace():
            raise ValueError("message cant be empty or just whitespace")
        if len(message) > 500:
            raise ValueError("message cant be longer than 500 characters")
        
        # send request
        response = await self.chat_protocol.send({
            "request_type": OpCode.USER_MESSAGE,
            "to_username": username,
            "message": message
        })

        # return sender username (user)
        return username

    # returns username
    async def whoami(self):
        # send request and retrieve username
        response = await self.chat_protocol.send({
            "request_type": OpCode.WHOAMI
        })
        username = response.get("username")
        if not username:
            raise RuntimeError("server returned empty username for whoami")
        
        # return username
        return username

    # returns the info of a specified user
    async def whois(self, username):
        #validate username
        username = username.strip() if username else ""
        if not username:
            raise ValueError("username cant be empty")
        
        # send request and safely save channels
        response = await self.chat_protocol.send({
            "request_type": OpCode.WHOIS,
            "username": username
        })
        if "channels" not in response:
            response["channels"] = []
        
        # return response dictionary
        return response

    # background task that causes event dataclasses to be made from relevant responses
    async def _dispatch_events(self):
        # continuously runs
        while True:
            try:
                # get an event from the queue
                event = await self.chat_protocol.event_queue.get()

                # update state if required
                if isinstance(event, UsernameChangeEvent):
                    if event.old_username == self.username:
                        self.username = event.new_username
                elif isinstance(event, ServerShutdownEvent):
                    self.session = None
                    self.chat_protocol.session = self.session
                    self.username = None
                    self.joined_channels = set()

                # pass event to callback method
                if self.on_event:
                    self.on_event(event)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"error dispatching event: {e}")
