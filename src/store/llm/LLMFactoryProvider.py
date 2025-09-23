from .providers import CohereProvider, OpenAiProvider
from .LLMEnums import LLMProviderType
from helpers import Settings

class LLMFactoryProvider:

    def __init__(self , config: Settings):
        self.config = config

    def create(self, provider):
        if provider == LLMProviderType.OPENAI.value:
            return OpenAiProvider(
                api_key = self.config.OPENAI_API_KEY,
                api_url = self.config.OPENAI_API_URL,
                default_input_max_characters = self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens = self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature = self.config.GENERATION_DEFAULT_TEMPERATURE
            )
        
        if provider == LLMProviderType.COHERE.value:
            return CohereProvider(
                api_key = self.config.COHERE_API_KEY,
               default_input_max_characters = self.config.INPUT_DEFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens = self.config.GENERATION_DEFAULT_MAX_TOKENS,
                default_generation_temperature = self.config.GENERATION_DEFAULT_TEMPERATURE
            )

        return None