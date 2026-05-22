# KRNRUA001

import ChatProtocol
from eventDataclasses import UsernameChangeEvent, ServerShutdownEvent
import asyncio

class ChatClient:

    def __init__(self, chat_protocol: ChatProtocol):
        self.chat_protocol = chat_protocol
        self.session = None
        self.username = None
        self.channels = set()
        self.on_event = None
        self.ping_task = None
        self.event_task = None

    async def connect(self):
        await self.chat_protocol.start()
        response = await self.chat_protocol.send({"request_type": 1})

        self.session = response.get("session")
        self.chat_protocol.session = self.session
        self.username = response.get("username")

        self.ping_task = asyncio.create_task(self.ping())
        self.event_task = asyncio.create_task(self.events())

        return response.get("message")

    async def ping(self):
        while True:
            try:
                await asyncio.sleep(30)
                await self.chat_protocol.send({"request_type": 3})
            except asyncio.CancelledError:
                break

    async def disconnect(self):
        if self.ping_task and not self.ping_task.done():
            self.ping_task.cancel()
        if self.event_task and not self.event_task.done():
            self.event_task.cancel()
        if not self.ping_task and not self.event_task and not self.session:
            print("already disconnected")
            return

        try:
            response = await asyncio.shield(self.chat_protocol.send({"request_type": 2}))
            return response.get("message")
        except Exception as e:
            return "failed to deliver disconnect message: {e}"
        finally:
            self.session = None
            self.chat_protocol.session = None
            self.username = None
            self.channels = set()

    async def create_channel(self, channel, description):
        pass

    async def list_channels(self):
        pass

    async def channel_info(self, channel):
        pass

    async def join_channel(self, channel):
        pass

    async def leave_channel(self, channel):
        pass

    async def message_channel(self, channel, message):
        pass

    async def set_username(self, username):
        pass

    async def list_users(self, channel=None):
        pass

    async def message_user(self, username, message):
        pass

    async def whoami(self):
        pass

    async def whois(self, username):
        pass

    async def events(self):
        while True:
            try:
                event = await self.chat_protocol.event_queue.get()

                if isinstance(event, UsernameChangeEvent):
                    if event.old_username == self.username:
                        self.username = event.new_username

                if isinstance(event, ServerShutdownEvent):
                    self.session = None
                    self.chat_protocol.session = self.session
                    self.username = None
                    self.channels = set()

                if self.on_event:
                    self.on_event(event)

            except asyncio.CancelledError:
                break
