from pydantic import Field
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application settings
    APP_NAME: str = "Document Analysis System"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = False
    LOG_LEVEL: str = "INFO"
    
    # FAISS Vector Store settings
    FAISS_INDEX_PATH: str = Field("./faiss_index", env="FAISS_INDEX_PATH")
    FAISS_DIMENSION: int = Field(1536, env="FAISS_DIMENSION")  # OpenAI embedding dimension
    FAISS_METRIC: str = Field("cosine", env="FAISS_METRIC")
    
    # LangChain settings
    LANGCHAIN_TRACING_V2: bool = Field(False, env="LANGCHAIN_TRACING_V2")
    LANGCHAIN_ENDPOINT: str = Field("", env="LANGCHAIN_ENDPOINT")
    LANGCHAIN_API_KEY: str = Field("", env="LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = Field("oozo", env="LANGCHAIN_PROJECT")
    
    # LLM settings - OpenAI compatible API
    OPENAI_API_KEY: str = Field("dummy_key_for_development", env="OPENAI_API_KEY")
    OPENAI_BASE_URL: str = Field("https://10f9698e-46b7-4a33-be37-f6495989f01f.modelrun.inference.cloud.ru", env="OPENAI_BASE_URL")
    OPENAI_MODEL: str = Field("qwen3:32b", env="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = Field(0.3, env="OPENAI_TEMPERATURE")
    OPENAI_MAX_TOKENS: int = Field(2000, env="OPENAI_MAX_TOKENS")
    
    # File upload settings
    MAX_FILE_SIZE: int = Field(10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: str = Field("pdf,docx,txt", env="ALLOWED_EXTENSIONS")
    UPLOAD_PATH: str = Field("./uploads", env="UPLOAD_PATH")
    
    # CORS settings
    CORS_ORIGINS: str = Field("http://localhost:3000,http://127.0.0.1:3000", env="CORS_ORIGINS")
    ALLOWED_HOSTS: str = Field("*", env="ALLOWED_HOSTS")
    
    @property
    def ALLOWED_EXTENSIONS_LIST(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(",")]
    
    @property
    def CORS_ORIGINS_LIST(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def ALLOWED_HOSTS_LIST(self) -> List[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
    
    # Security settings
    SECRET_KEY: str = Field("your_secret_key_here_change_in_production", env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Redis settings
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # Document processing settings
    MAX_DOCUMENT_PAGES: int = Field(50, env="MAX_DOCUMENT_PAGES")
    PROCESSING_TIMEOUT: int = Field(300, env="PROCESSING_TIMEOUT")  # 5 minutes
    CHUNK_SIZE: int = Field(1000, env="CHUNK_SIZE")
    
    # LLM analysis settings
    ANALYSIS_BATCH_SIZE: int = Field(10, env="ANALYSIS_BATCH_SIZE")
    RETRY_ATTEMPTS: int = Field(3, env="RETRY_ATTEMPTS")
    RATE_LIMIT_REQUESTS: int = Field(100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(60, env="RATE_LIMIT_WINDOW")
    
    # Logging settings
    LOG_FILE: str = Field("./logs/app.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True) 