# KRNRUA001

from dataclasses import dataclass

@dataclass
class UserMessageEvent:
    username: str
    message: str

@dataclass
class ChannelMessageEvent:
    channel: str
    username: str
    message: str

@dataclass
class UserJoinEvent:
    channel: str
    username: str
    description: str

@dataclass
class UserLeaveEvent:
    channel: str
    username: str

@dataclass
class UsernameChangeEvent:
    old_username: str
    new_username: str

@dataclass
class ServerMessageEvent:
    message: str

@dataclass
class ServerShutdownEvent:
    message: str