from app.services.llm_service_interface import LLMServiceInterface
from app.services.openai_service import OpenAIService
from app.services.llama_service import LlamaService
# from app.services.llama_service_remote import LlamaService
# from app.services.claude_service import ClaudeService

class LLMFactory:
    @staticmethod
    def create_llm_service(model_option: str) -> LLMServiceInterface:
        if model_option.lower() == "openai":
            return OpenAIService(model_name="gpt-4o")
        elif model_option.lower() == "llama":
            return LlamaService()
        # elif model_option.lower() == "claude":
        #     return ClaudeService()
        else:
            raise ValueError(f"Unsupported LLM model: {model_option}")