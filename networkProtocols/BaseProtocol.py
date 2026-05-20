# KRNRUA001

from abc import ABC, abstractmethod

class BaseProtocol:

    @abstractmethod
    async def start(on_response):
        pass

    @abstractmethod
    def send(data: bytes):
        pass

    @abstractmethod
    def close():
        pass