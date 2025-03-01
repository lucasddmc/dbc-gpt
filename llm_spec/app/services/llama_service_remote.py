import os
import logging
from groq import Groq  
from app.services.llm_service_interface import LLMServiceInterface

logger = logging.getLogger(__name__)

class LlamaService(LLMServiceInterface):
    def __init__(self):
        # Initialize the Groq client
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model_generator_name = "llama-3.1-70b-versatile"
        self.model_verifier_name = "llama-3.1-8b-instant"

    def send_message(self, message_content: str) -> str:
        try:
            # Create the chat completion with the given message
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Given an ERC interface and an EIP markdown,  generate a specification for the ERC interface with solc-verify postconditions annotations."},
                    {"role": "user", "content": message_content}
                ],
                model=self.model_generator_name,
            )
            completion = response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error communicating with Groq API: {e}")
            return ""
        
        return completion