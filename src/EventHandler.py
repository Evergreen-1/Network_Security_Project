import asyncio
from datetime import datetime
from src.eventDataclasses import (
    ChannelMessageEvent,
    UserMessageEvent,
    ChannelJoinEvent,
    ChannelLeaveEvent,
    UsernameChangeEvent,
    ServerMessageEvent,
    ServerShutdownEvent,
)

class Handler():
    def __init__(self, controller, updateMessages):
        self.controller = controller
        self.updateMessages = updateMessages
        
        self.EVENT_HANDLERS = {
            ChannelMessageEvent:  self.onChannelMessage,
            UserMessageEvent:     self.onDirectMessage,
            ChannelJoinEvent:     self.onUserJoin,
            ChannelLeaveEvent:    self.onUserLeave,
            UsernameChangeEvent:  self.onUsernameChange,
            ServerMessageEvent:   self.onServerMessage,
            ServerShutdownEvent:  self.onServerShutdown,
        }

    def onChannelMessage(self, event: ChannelMessageEvent):
        msgTime = datetime.now().strftime("%H:%M:%S")
        if event.channel in self.controller.chatsWithChannels:
            i = 0
            while self.controller.channelMessages[i][0] != event.channel:
                i+=1
            self.controller.channelMessages[i][1].append({"sender":event.username, "text": event.message, "time":msgTime})
            if self.controller.showChannel == True and self.controller.currentChat == event.channel:
                self.updateMessages(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.channelMessages[i][1])        
        print(f"[{event.channel}] {event.username}: {event.message}")

    def onDirectMessage(self, event: UserMessageEvent):
        msgTime = datetime.now().strftime("%H:%M:%S")
        if (not (event.username in self.controller.chatsWithUsers)):
            self.controller.chatsWithUsers.append(event.username)
            self.controller.userMessages.append((event.username, [{"sender":event.username, "text": event.message, "time":msgTime}]))
        else:
            i = 0
            while (self.controller.userMessages[i][0] != event.username):
                i += 1
            self.controller.userMessages[i][1].append({"sender":event.username, "text": event.message, "time":msgTime})
            if self.controller.showChannel == False and self.controller.currentChat == event.username:
                self.updateMessages(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.userMessages[i][1])
        print(f"[DM from {event.username}]: {event.message}")

    def onUserJoin(self, event: ChannelJoinEvent):
        msgTime = datetime.now().strftime("%H:%M:%S")
        print(f"{event.username} joined #{event.channel}")
        i = 0
        while (self.controller.channelMessages[i][0] != event.channel):
            i += 1
        text = event.username + " has joined the channel "  + event.channel
        self.controller.channelMessages[i][1].append({"sender":"", "text": text, "time":msgTime})
        if self.controller.showChannel == True and self.controller.currentChat == event.channel:
            self.updateMessages(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.channelMessages[i][1])

    def onUserLeave(self, event: ChannelLeaveEvent):
        msgTime = datetime.now().strftime("%H:%M:%S")
        print(f"{event.username} left #{event.channel}")
        i = 0
        while (self.controller.channelMessages[i][0] != event.channel):
            i += 1
        text = event.username + " has left the channel "  + event.channel
        self.controller.channelMessages[i][1].append({"sender":"", "text": text, "time":msgTime})
        if self.controller.showChannel == True and self.controller.currentChat == event.channel:
            self.updateMessages(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.channelMessages[i][1])

    def onUsernameChange(self, event: UsernameChangeEvent):
        for msg in self.controller.userMessages:
            if msg[0] == event.old_username:
                msg[0] == event.new_username
                for text in msg[1]:
                    if text["sender"] == event.old_username:
                        text["sender"] = event.new_username
                break
        for channelMsgs in self.controller.userMessages:
            for text in channelMsgs[1]:
                if text["sender"] == event.old_username:
                    text["sender"] = event.new_username
        print(f"{event.old_username} is now known as {event.new_username}")

    def onServerMessage(self, event: ServerMessageEvent):
        msgTime = datetime.now().strftime("%H:%M:%S")
        self.controller.channelMessages[0][1].append({"sender":"Server", "text": event.message, "time":msgTime})
        if self.controller.showChannel == True and self.controller.currentChat == event.channel:
            self.updateMessages(self.controller.frames["ChattingFrame"].msgListFrame.messageListFrame, self.controller, self.controller.channelMessages[0][1])
        print(f"[SERVER]: {event.message}")

    def onServerShutdown(self, event: ServerShutdownEvent):
        asyncio.create_task(self.controller.exitChattingApp())
        print(f"[SERVER SHUTTING DOWN]: {event.message}")    

    def handleEvent(self, event):
        handler = self.EVENT_HANDLERS.get(type(event))
        if handler:
            handler(event)
        else:
            print(f"[UNHANDLED EVENT]: {type(event).__name__}")


