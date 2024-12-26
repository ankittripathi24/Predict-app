from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/sensordb"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()