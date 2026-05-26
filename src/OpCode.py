# KRNRUA001
# int enum class containing all request and response opcodes
# (no magic numbers :])

from enum import IntEnum

class OpCode(IntEnum):
    # requests
    CONNECT = 1
    DISCONNECT = 2
    PING = 3
    CHANNEL_CREATE = 4
    CHANNEL_LIST = 5
    CHANNEL_INFO = 6
    CHANNEL_JOIN = 7
    CHANNEL_LEAVE = 8
    CHANNEL_MESSAGE = 9
    WHOIS = 10
    WHOAMI = 11
    USER_MESSAGE = 12
    SET_USERNAME = 13
    USER_LIST = 14

    # responses
    ERROR = 20
    OK = 21
    CONNECT_RESP = 22
    DISCONNECT_RESP = 23
    PING_RESP = 24
    CHANNEL_CREATE_RESP = 25
    CHANNEL_LIST_RESP = 26
    CHANNEL_INFO_RESP = 27
    CHANNEL_JOIN_RESP = 28
    CHANNEL_LEAVE_RESP = 29
    CHANNEL_MESSAGE_RESP = 30
    WHOIS_RESP = 31
    WHOAMI_RESP  = 32
    USER_MESSAGE_RESP = 33
    SET_USERNAME_RESP = 34
    USER_LIST_RESP = 35
    SERVER_MESSAGE = 36
    SERVER_SHUTDOWN = 37