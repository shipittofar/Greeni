from abc import ABC, abstractmethod

class BaseSMSService(ABC):
    def __init__(self, api_key: str, sender: str):
        self.api_key = api_key
        self.sender = sender

    @abstractmethod
    def send(self, message: str, mobile: str):
        pass
