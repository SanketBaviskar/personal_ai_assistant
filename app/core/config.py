from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Exo"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "changethis-secret-key-for-dev-only-123456"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    ALGORITHM: str = "HS256"
    
    # Regex to match: localhost (3000/5173/8000) OR https://exo-drab-zeta.vercel.app (with/without slash)
    BACKEND_CORS_ORIGINS: List[str] = [] # Deprecated in favor of regex for flexibility
    # This regex allows the specific frontend URL and localdev
    BACKEND_CORS_ORIGIN_REGEX: str = r"^(http://localhost:\d+|https://exo-drab-zeta\.vercel\.app)/?$"

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
