from abc import ABC, abstractmethod

class LLMServiceInterface(ABC):
    @abstractmethod
    def send_message(self, message_content: str) -> str:
        pass