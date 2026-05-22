# KRNRUA001

from abc import ABC, abstractmethod

class BaseProtocol:

    @abstractmethod
    async def start(self, on_response):
        pass

    @abstractmethod
    def send(self, data: bytes):
        pass

    @abstractmethod
    def close(self):
        pass