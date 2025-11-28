from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Personal AI Knowledge Assistant"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "changethis-secret-key-for-dev-only-123456" # TODO: Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8 # 8 days
    ALGORITHM: str = "HS256"
    
    # Database
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./sql_app.db"

    # Vector DB
    VECTOR_DB_TYPE: str = "chroma"
    CHROMA_DB_PATH: str = "./chroma_db"

    class Config:
        env_file = ".env"

settings = Settings()
