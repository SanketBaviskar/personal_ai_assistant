from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Exo"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "changethis-secret-key-for-dev-only-123456"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ALGORITHM: str = "HS256"
    
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "https://exo-drab-zeta.vercel.app"]

    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./sql_app.db"
    DATABASE_URL: Optional[str] = None

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("postgres://", "postgresql://")
        return self.SQLALCHEMY_DATABASE_URI


    VECTOR_DB_TYPE: str = "chroma"
    CHROMA_DB_PATH: str = "./chroma_db"

    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    HUGGINGFACE_API_KEY: Optional[str] = None
    HUGGINGFACE_MODEL: str = "Qwen/Qwen2.5-72B-Instruct"

    class Config:
        env_file = ".env"

settings = Settings()
