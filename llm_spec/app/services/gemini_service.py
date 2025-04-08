import os
import logging
from dotenv import load_dotenv
from app.services.llm_service_interface import LLMServiceInterface
from google import genai

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiService(LLMServiceInterface):
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.model_name = model_name
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set in environment variables")
        self.client = genai.Client(api_key=self.api_key)
        logger.info(f"Initialized GeminiService with model {model_name}")

    def send_message(self, message_content: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=message_content,
            )
            return response.text
        except Exception as e:
            logger.error(f"GeminiService error: {e}")
            raise