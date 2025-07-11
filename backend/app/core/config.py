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
    
    # Database settings
    POSTGRES_HOST: str = Field(..., env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(5432, env="POSTGRES_PORT")
    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # OpenAI settings
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field("gpt-4", env="OPENAI_MODEL")
    OPENAI_TEMPERATURE: float = Field(0.3, env="OPENAI_TEMPERATURE")
    OPENAI_MAX_TOKENS: int = Field(2000, env="OPENAI_MAX_TOKENS")
    
    # File upload settings
    MAX_FILE_SIZE: int = Field(10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_EXTENSIONS: str = Field("pdf,docx,txt", env="ALLOWED_EXTENSIONS")
    UPLOAD_PATH: str = Field("/app/uploads", env="UPLOAD_PATH")
    
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
    
    # Redis settings (optional)
    REDIS_HOST: str = Field("redis", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    
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
    LOG_FILE: str = Field("/app/logs/app.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True) 