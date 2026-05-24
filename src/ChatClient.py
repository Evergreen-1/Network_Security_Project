# KRNRUA001

from src.ChatProtocol import ChatProtocol
from src.eventDataclasses import UsernameChangeEvent, ServerShutdownEvent
import asyncio
from src.OpCode import OpCode

class ChatClient:

    def __init__(self, chat_protocol: ChatProtocol):
        self.chat_protocol = chat_protocol
        self.session = None
        self.username = None
        self.joined_channels = set()
        self.on_event = None
        self.ping_task = None
        self.event_task = None

    async def connect(self):
        await self.chat_protocol.start()
        response = await self.chat_protocol.send({
            "request_type": OpCode.CONNECT
            })

        self.session = response.get("session", None)
        if not self.session:
            raise RuntimeError("server did not return a session")
        
        self.chat_protocol.session = self.session
        self.username = response.get("username")

        self.ping_task = asyncio.create_task(self._ping())
        self.event_task = asyncio.create_task(self._dispatch_events())

        return response.get("message")

    async def _ping(self):
        while True:
            try:
                await asyncio.sleep(30)
                await self.chat_protocol.send({
                    "request_type": OpCode.PING
                    })
            except asyncio.CancelledError:
                break
            except Exception as e:  # TODO: maybe also notify UI with an event?
                print(f"ping failed: {e}")

    async def disconnect(self):
        if not self.session:
            return "already disconnected"
        
        if self.ping_task and not self.ping_task.done():
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass

        if self.event_task and not self.event_task.done():
            self.event_task.cancel()
            try:
                await self.event_task
            except asyncio.CancelledError:
                pass

        # response = await asyncio.shield(self.chat_protocol.send({
        #     "request_type": OpCode.DISCONNECT
        #     }))
        # self.session = None
        # self.chat_protocol.session = None
        # self.username = None
        # self.joined_channels = set()
        # self.chat_protocol.close()
        # return response.get("message") or "disconnected"

        try:
            response = await asyncio.shield(self.chat_protocol.send({
                "request_type": OpCode.DISCONNECT
                }))
            return response.get("message") or "disconnected"
        except Exception as e:
            return f"failed to deliver disconnect message: {e}"
        finally:
            self.session = None
            self.chat_protocol.session = None
            self.username = None
            self.joined_channels = set()
            self.chat_protocol.close()

    async def create_channel(self, channel, description):
        channel = channel.strip() if channel else ""
        if not channel:
            raise ValueError("channel name cant be empty")
        if len(channel) > 20:
            raise ValueError("channel name cant be longer than 20 characters")
        
        description = description.strip() if description else ""
        if not description:
            raise ValueError("description cant be empty")
        if len(description) > 100:
            raise ValueError("description cant be longer than 100 characters")
        
        response = await self.chat_protocol.send({
            "request_type": OpCode.CHANNEL_CREATE,
            "channel": channel,
            "description": description
        })
        self.joined_channels.add(channel)
        return response
        
        # try:
        #     response = await self.chat_protocol.send({
        #         "request_type": 4,
        #         "channel": channel,
        #         "description": description
        #     })
        #     self.joined_channels.add(channel)
        #     return response
        # except RuntimeError as e:
        #     print(f"couldnt create channel: {e}")
        #     return {
        #         "success": False,
        #         "channel": channel,
        #         "error": str(e)
        #     }

    async def list_channels(self):
        channels = []
        offset = 0
        max_pages = 100
        page_count = 0

        while page_count < max_pages:
            request = {"request_type": OpCode.CHANNEL_LIST}
            if offset > 0:
                request["offset"] = offset
            response = await self.chat_protocol.send(request)

            received_channels = response.get("channels", [])
            if received_channels:
                channels.extend(received_channels)

            if not response.get("next_page"):
                break

            offset += 10
            page_count += 1
        
        return channels

    async def channel_info(self, channel):
        channel = channel.strip() if channel else ""
        if not channel:
            raise ValueError("channel name cant be empty")
        if len(channel) > 20:
            raise ValueError("channel name cant be longer than 20 characters")
        
        response = await self.chat_protocol.send({
            "request_type": OpCode.CHANNEL_INFO,
            "channel": channel
        })
        if "members" not in response:
            response["members"] = []
        return response

        # try:
        #     response = await self.chat_protocol.send({
        #         "request_type": 6,
        #         "channel": channel
        #     })
        #     if "members" not in response:
        #         response["members"] = []
        #     return response
        # except RuntimeError as e:
        #     print(f"failed to get channel info: {e}")
        #     return {
        #         "success": False,
        #         "channel": channel,
        #         "error": str(e)
        #     }

    async def join_channel(self, channel):
        channel = channel.strip() if channel else ""
        if not channel:
            raise ValueError("channel name cant be empty")
        if len(channel) > 20:
            raise ValueError("channel name cant be longer than 20 characters")
        
        response = await self.chat_protocol.send({
            "request_type": OpCode.CHANNEL_JOIN,
            "channel": channel
        })
        self.joined_channels.add(channel)
        return response
        
        # try:
        #     response = await self.chat_protocol.send({
        #         "request_type": 7,
        #         "channel": channel
        #     })
        #     self.joined_channels.add(channel)
        #     return response
        # except RuntimeError as e:
        #     print(f"couldnt join channel: {e}")
        #     return {
        #         "success": False,
        #         "channel": channel,
        #         "error": str(e)
        #     }
        
    async def leave_channel(self, channel):
        channel = channel.strip() if channel else ""
        if not channel:
            raise ValueError("channel name cant be empty")
        if len(channel) > 20:
            raise ValueError("channel name cant be longer than 20 characters")
        
        response = await self.chat_protocol.send({
            "request_type": OpCode.CHANNEL_LEAVE,
            "channel": channel
        })
        self.joined_channels.discard(channel)
        return response
        
        # try:
        #     response = await self.chat_protocol.send({
        #         "request_type": 8,
        #         "channel": channel
        #     })
        #     self.joined_channels.discard(channel)
        #     return response
        # except RuntimeError as e:
        #     print(f"couldnt leave channel: {e}")
        #     return {
        #         "success": False,
        #         "channel": channel,
        #         "error": str(e)
        #     }

    async def message_channel(self, channel, message):
        channel = channel.strip() if channel else ""
        if not channel:
            raise ValueError("channel name cant be empty")
        if len(channel) > 20:
            raise ValueError("channel name cant be longer than 20 characters")
        
        if not message or message.isspace():
            raise ValueError("message cant be empty or just whitespace")
        if len(message) > 500:
            raise ValueError("message cant be longer than 500 characters")
        
        response = await self.chat_protocol.send({
            "request_type": OpCode.CHANNEL_MESSAGE,
            "channel": channel,
            "message": message
        })
        return response
        
        # try:
        #     response = await self.chat_protocol.send({
        #         "request_type": 9,
        #         "channel": channel,
        #         "message": message
        #     })
        #     return response
        # except RuntimeError as e:
        #     print(f"couldnt message channel: {e}")
        #     return {
        #         "success": False,
        #         "channel": channel,
        #         "error": str(e)
        #     }

    async def set_username(self, username):
        username = username.strip() if username else ""
        if not username:
            raise ValueError("username cant be empty")
        if self.chat_protocol.is_cleartext and not username.startswith("clear-"):
            raise ValueError("cleartext usernames have to start with 'clear-'")
        if ':' in username:
            raise ValueError("cant have colon in username")
        if len(username) > 20:
            raise ValueError("username cant be longer than 20 characters")
        
        response = await self.chat_protocol.send({
            "request_type": OpCode.SET_USERNAME,
            "username": username
        })
        self.username = response.get("new_username") or self.username
        return self.username
        
        # try:
        #     response = await self.chat_protocol.send({
        #         "request_type": 13,
        #         "username": username
        #     })
        #     old_username = self.username
        #     self.username = response.get("new_username") or self.username
        #     return {
        #         "old_username": old_username,
        #         "new_username": self.username
        #     }
        # except RuntimeError as e:
        #     print(f"couldnt join channel: {e}")
        #     return {
        #         "success": False,
        #         "username": username,
        #         "error": str(e)
        #     }

    async def list_users(self, channel=None):
        if channel:
            channel = channel.strip() if channel else ""
            if len(channel) > 20:
                raise ValueError("channel name cant be longer than 20 characters")

        users = []
        offset = 0
        max_pages = 50
        page_count = 0

        while page_count < max_pages:
            request = {"request_type": OpCode.USER_LIST}
            if channel:
                request["channel"] = channel
            if offset > 0:
                request["offset"] = offset
            response = await self.chat_protocol.send(request)

            received_users = response.get("users", [])
            if received_users:
                users.extend(received_users)

            if not response.get("next_page"):
                break

            offset += 20
            page_count += 1
        
        return users

    async def message_user(self, username, message):
        username = username.strip() if username else ""
        if not username:
            raise ValueError("username cant be empty")
        if self.chat_protocol.is_cleartext and not (username.startswith("clear-") or username.startswith("cleartext_user_")):
            raise ValueError("cleartext usernames have to start with 'clear-'")
        if ':' in username:
            raise ValueError("cant have colon in username")
        if len(username) > 23:
            raise ValueError("username cant be longer than 20 characters")
        
        if not message or message.isspace():
            raise ValueError("message cant be empty or just whitespace")
        if len(message) > 500:
            raise ValueError("message cant be longer than 500 characters")
        
        response = await self.chat_protocol.send({
            "request_type": OpCode.USER_MESSAGE,
            "to_username": username,
            "message": message
        })

        return username
        
        # try:
        #     response = await self.chat_protocol.send({
        #         "request_type": 12,
        #         "to_username": username,
        #         "message": message
        #     })
        #     return response
        # except RuntimeError as e:
        #     print(f"couldnt message user: {e}")
        #     return {
        #         "success": False,
        #         "username": username,
        #         "error": str(e)
        #     }

    async def whoami(self):
        response = await self.chat_protocol.send({
            "request_type": OpCode.WHOAMI
        })
        username = response.get("username")
        if not username:
            raise RuntimeError("server returned empty username for whoami")
        return username

    async def whois(self, username):
        username = username.strip() if username else ""
        if not username:
            raise ValueError("username cant be empty")
        
        response = await self.chat_protocol.send({
            "request_type": OpCode.WHOIS,
            "username": username
        })
        if "channels" not in response:
            response["channels"] = []
        return response
        
        # try:
        #     response = await self.chat_protocol.send({
        #         "request_type": 10,
        #         "username": username
        #     })
        #     if "channels" not in response:
        #         response["channels"] = []
        #     return response
        # except RuntimeError as e:
        #     print(f"couldnt join channel: {e}")
        #     return {
        #         "success": False,
        #         "username": username,
        #         "error": str(e)
        #     }

    async def _dispatch_events(self):
        while True:
            try:
                event = await self.chat_protocol.event_queue.get()

                if isinstance(event, UsernameChangeEvent):
                    if event.old_username == self.username:
                        self.username = event.new_username
                elif isinstance(event, ServerShutdownEvent):
                    self.session = None
                    self.chat_protocol.session = self.session
                    self.username = None
                    self.joined_channels = set()

                if self.on_event:
                    self.on_event(event)

            except asyncio.CancelledError:
                break

            except Exception as e:
                print(f"error dispatching event: {e}")
