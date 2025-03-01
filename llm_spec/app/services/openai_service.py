import openai, os, time, logging
from dotenv import load_dotenv
from app.services.llm_service_interface import LLMServiceInterface

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

logger = logging.getLogger(__name__)

class Assistant:
    def __init__(self, id) -> None:
        self.id = id

class Thread:
    def __init__(self, assistant: Assistant) -> None:
        self.assistant = assistant
        self._thread = openai.beta.threads.create()
    
    @property
    def id(self):
        return self._thread.id
    
    def send_message(self, content: str) -> 'Interaction':
        interaction = Interaction(self, content)
        return interaction
    
    @property
    def last_message(self) -> str:
        response = openai.beta.threads.messages.list(
            thread_id=self.id
        )
        # Returns last response from thread
        return response.data[0].content[0].text.value

class Interaction:
    def __init__(self, thread: Thread, prompt: str) -> None:
        self.thread = thread
        self.prompt = prompt
        self._create_message()
        self._create_run()

    def _create_message(self):
        openai.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=self.prompt
        )
    
    def _create_run(self):
        self._run = openai.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.thread.assistant.id,
        )
    
    @property
    def id(self):
        return self._run.id
    
    def remote_sync(self):
        self._run = openai.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=self._run.id
        )
    
    @property
    def status(self):
        return self._run.status

    def await_for_response(self) -> str:
        status = self.status
        while status != "completed":
            self.remote_sync()
            status = self.status
            print(f"Awaiting for a response. Status: {status}")
            time.sleep(5)
        return self.thread.last_message

class OpenAIService(LLMServiceInterface):
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
        self.assistant_id = os.getenv('ASSISTANT_ID')
        if not self.assistant_id:
            raise ValueError("ASSISTANT_ID not set in environment variables")
        self.assistant = Assistant(self.assistant_id)
        self.thread = Thread(self.assistant)

    def send_message(self, message_content: str) -> str:
        interaction = self.thread.send_message(message_content)
        response = interaction.await_for_response()
        return response