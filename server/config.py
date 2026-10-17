from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # Server
    environment: str = "development"
    server_port: int = 8000

    # Firebase
    firebase_project_id: str = ""

    # Gemini
    gemini_api_key: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
