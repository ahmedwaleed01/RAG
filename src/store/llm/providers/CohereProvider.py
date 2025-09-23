from ..LLMInterface import LLMInterface
import logging
from ..LLMEnums import CohereEnums , DocumentType
import cohere

class CohereProvider(LLMInterface):

    def __init__(self, api_key: str,
                 default_input_max_characters: int = 1000,
                 default_generation_max_output_tokens: int = 1000,
                 default_generation_temperature: float = 0.1):

        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None
        self.embedding_model_id = None

        self.embedding_size = None

        self.client = cohere.Client(api_key= api_key)

        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int ):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def generate_text(self, prompt: str, max_output_tokens: int = None, temperature: int = None, chat_history: list = []):
        is_valid = self.validate_model()

        if is_valid is None:
            return None

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        response = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            messages = self.process_text(prompt),
            temperature = temperature,
            max_tokens = max_output_tokens
        )
        

        return response.text
    
    def embed_text(self, text:str,document_type: str = None):
        is_valid = self.validate_model_embedding()

        if is_valid is None:
            return None
        
        input_type = CohereEnums.DOCUMENT.value 

        if document_type == DocumentType.QUERY.value:
            input_type = CohereEnums.QUERY.value
        

        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type = input_type,
            embedding_types = ["float"],
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("No response from Cohere API.")
            return None
        
        return response.embeddings.float[0]

    
    def validate_model(self):
        if self.client is None:
            self.logger.error("Cohere client is not initialized.")
            return None
        
        if self.generation_model_id is None:
            self.logger.error("Generation model is not set.")
            return None
        
        if self.embedding_model_id is None:
            self.logger.error("Embedding model is not set.")
            return None
        
        return True
    
    def validate_model_embedding(self):
        if self.client is None:
            self.logger.error("Cohere client is not initialized.")
            return None

        if self.embedding_model_id is None:
            self.logger.error("Embedding model is not set.")
            return None
        
        return True

    
    def process_text(self, text: str):
        return text[:self.default_input_max_characters].strip()
    
    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "text": self.process_text(prompt)
        }

