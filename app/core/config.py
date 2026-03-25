from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL= str
    SUPABASE_URL=str
    SUPABASE_SERVICE_ROLE_KEY=str
    QDRANT_API_KEY=str
    OPENAI_API_KEY=str
    COLLECTION_NAME=str
    QDRANT_URL=str
    REDIS_URL=str
    
    class Config:
        env_file = ".env"

settings = Settings()