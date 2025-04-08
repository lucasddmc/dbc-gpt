import logging
from app.services.llm_service_interface import LLMServiceInterface
from ollama import chat, ChatResponse

logger = logging.getLogger(__name__)

class OllamaService(LLMServiceInterface):
    """"
    Para rodar, é necessário instalar o Ollama e baixar o modelo:
    ```
    ollama pull deepseek-coder-v2:16b
    ```
    Para rodar o Ollama, use (linux):
    ```
    ollama serve &
    ```
    """
    def __init__(self, model_name: str = "deepseek-coder-v2:16b"):
        print("init")
        self.model_name = model_name
        logger.info(f"Using local Ollama model: {self.model_name}")

    def send_message(self, prompt: str) -> str:
        try:
            # print("startou")
            # logger.debug(f"Sending prompt to Ollama: {prompt}")
            # response = ollama.chat(
            #     model=self.model_name,
            #     messages=[{'role': 'user', 'content': prompt}]
            # )

            response: ChatResponse = chat(model=self.model_name, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            # print(response['message']['content'])
            # or access fields directly from the response object
            # print(response.message.content)
            # print("recebi")

            reply = response["message"]["content"]
            logger.debug(f"Received response from Ollama: {reply}")
            # print("reply")
            return reply
        except Exception as e:
            logger.error(f"Error during Ollama message generation: {e}")
            raise e
