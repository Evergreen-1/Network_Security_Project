# KRNRUA001
# abstract class that allows higher levels to interface
# with lower levels without having to know which
# specific protocol is being used

from abc import ABC, abstractmethod

class BaseProtocol(ABC):

    def __init__(self):
        self.is_cleartext = False

    @abstractmethod
    async def start(self, on_response):
        pass

    @abstractmethod
    def send(self, data: bytes):
        pass

    @abstractmethod
    def close(self):
        pass