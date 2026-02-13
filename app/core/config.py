from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Greeni Backend"

    TELEGRAM_ENABLED: bool = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
    TELEGRAM_SUPERUSER_ID: str = os.getenv("TELEGRAM_SUPERUSER_ID", "")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SMS_PENDING_TEMPLATE: str = "device_pending"

    REDIS_URL: str = os.getenv("CELERY_BROKER_URL")

    SERVER_HOST: str = os.getenv("SERVER_HOST", "http://localhost:8000")

settings = Settings()
