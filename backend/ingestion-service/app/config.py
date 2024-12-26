from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "BVV6Hty6bZ"
    
    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TIMEOUT: int = 60
    
    # Service settings
    SERVICE_NAME: str = "iot-service"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"


