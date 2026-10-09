from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CodePilot API"
    DATABASE_URL: str = "sqlite:///./codepilot.db"
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    GITHUB_TOKEN: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    MAX_AGENT_ITERATIONS: int = 5
    SANDBOX_TIMEOUT: int = 60
    MAX_FILE_SIZE_MB: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
