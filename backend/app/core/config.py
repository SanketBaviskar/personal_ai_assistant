from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Personal AI Knowledge Assistant"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "changethis-secret-key-for-dev-only-123456" # TODO: Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days
    ALGORITHM: str = "HS256"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    
    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./sql_app.db"


    # Vector DB
    VECTOR_DB_TYPE: str = "chroma"
    CHROMA_DB_PATH: str = "./chroma_db"

    # Google
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    # GOOGLE_API_KEY: Optional[str] = None

    # Hugging Face
    HUGGINGFACE_API_KEY: Optional[str] = None
    HUGGINGFACE_MODEL: str = "Qwen/Qwen2.5-72B-Instruct"

    class Config:
        env_file = ".env"

settings = Settings()
