from abc import ABC, abstractmethod

class VerifierServiceInterface(ABC):
    @abstractmethod
    def verify(self, solidity_code: str, template_path: str, merge_output_path: str) -> (int, str):
        pass