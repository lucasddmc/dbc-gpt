# import os
# import logging
# from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
# from trl import setup_chat_format
# from app.services.llm_service_interface import LLMServiceInterface
# from huggingface_hub import login

# logger = logging.getLogger(__name__)

# class LlamaServicee(LLMServiceInterface):
#     """
#     LlamaService loads the fine-tuned Llama model (previously merged and pushed to Hugging Face Hub)
#     and performs local inference.
#     """
#     def __init__(self, model_name: str = "gabrielnogueiralt/llama-3.1-8B-transformers-single"):
#         self.model_name = model_name
        
#         # Automatically log in to Hugging Face Hub using the secret token from the environment variable.
#         token = os.getenv("HUGGING_FACE_LOGIN")
#         if token:
#             logger.info("HUGGING_FACE_LOGIN token found. Logging into Hugging Face Hub...")
#             login(token=token)
#         else:
#             logger.warning("HUGGING_FACE_LOGIN not set. Proceeding without automatic login.")
        
#         try:
#             logger.info(f"Loading fine-tuned Llama model: {model_name}")

#             # Configure quantization and CPU offload.
#             quantization_config = BitsAndBytesConfig(
#                 load_in_8bit=True,
#                 llm_int8_enable_fp32_cpu_offload=True
#             )

#             self.tokenizer = AutoTokenizer.from_pretrained(model_name)
#             self.model = AutoModelForCausalLM.from_pretrained(
#                 model_name,
#                 quantization_config=quantization_config,
#                 # Use a balanced device map that offloads some layers to the CPU, which is recommended
#                 # for GPUs with limited memory (like an RTX 4050 with 6GB).
#                 device_map="balanced_low_0"
#             )

#             # Optional: Set up the chat format if your model was fine-tuned for chat-based interaction.
#             self.model, self.tokenizer = setup_chat_format(self.model, self.tokenizer)
#             logger.info("Llama model and tokenizer loaded successfully.")
#         except Exception as e:
#             logger.error(f"Error loading Llama model: {e}")
#             raise e

#     def send_message(self, prompt: str) -> str:
#         """
#         Accepts a prompt string and returns the generated response as a string.
#         """
#         try:
#             # Tokenize the prompt, ensuring proper padding and truncation.
#             inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
#             # Move tensors to the same device as the model.
#             inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

#             # Generate a response from the model. Adjust max_length, temperature, etc., as needed.
#             outputs = self.model.generate(
#                 **inputs,
#                 max_length=2048,
#                 do_sample=True,
#                 temperature=0.7,
#                 num_return_sequences=1
#             )
#             # Decode the output while skipping special tokens.
#             response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
#             return response
#         except Exception as e:
#             logger.error(f"Error during Llama message generation: {e}")
#             raise e


import logging
from app.services.llm_service_interface import LLMServiceInterface
from ollama import chat, ChatResponse

logger = logging.getLogger(__name__)

class LlamaService(LLMServiceInterface):
    """
    LlamaService now wraps a local Ollama model instead of using Hugging Face.
    Make sure the model is pulled via `ollama pull <model>` and running locally.
    """
    def __init__(self, model_name: str = "llama3.2-4k"):
        print("init")
        self.model_name = model_name
        logger.info(f"Using local Ollama model: {self.model_name}")

    def send_message(self, prompt: str) -> str:
        """
        Accepts a prompt string and returns the generated response using the Ollama model.
        """
        try:
            print("startou")
            # logger.debug(f"Sending prompt to Ollama: {prompt}")
            # response = ollama.chat(
            #     model=self.model_name,
            #     messages=[{'role': 'user', 'content': prompt}]
            # )

            response: ChatResponse = chat(model='llama3.2-4k', messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            print(response['message']['content'])
            # or access fields directly from the response object
            print(response.message.content)
            print("recebi")

            reply = response["message"]["content"]
            logger.debug(f"Received response from Ollama: {reply}")
            print("reply")
            return reply
        except Exception as e:
            logger.error(f"Error during Ollama message generation: {e}")
            raise e
