from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    FILE_ALLOWED_EXTENSIONS:list[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE:int
    
    MONGODB_URL: str
    MONGODB_DATABASE: str

    EMBEDDING_BACKEND: str
    GENERATION_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None
    INPUT_DEFAULT_MAX_CHARACTERS: int = None
    GENERATION_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPERATURE: float = None

    VECTOR_DB_BACKEND: str = None
    VECTOR_DB_PATH: str = None
    VECTOR_DB_DISTANCE_METHOD: str = None

    DEFAULT_LANGUAGE: str = "en"

    JWT_SECRET: str

    class Config:
        env_file = ".env"
        
def get_settings() -> Settings:
    return Settings()
