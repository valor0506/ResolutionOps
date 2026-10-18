import logging
import os
from typing import Optional
from google import genai
from server.config import settings

logger = logging.getLogger("resolutionops.ai")


class GeminiClientManager:
    """Manages the official Google Gen AI SDK client and tracks API availability."""

    def __init__(self):
        self._client: Optional[genai.Client] = None
        self._initialized: bool = False
        self._api_key: str = (
            settings.gemini_api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
            or ""
        )

    def get_client(self) -> Optional[genai.Client]:
        """Returns the Gemini SDK client if API key is configured, else None."""
        if not self._initialized:
            if self._api_key:
                try:
                    self._client = genai.Client(api_key=self._api_key)
                    logger.info("Google Gen AI SDK client initialized successfully.")
                except Exception as e:
                    logger.warning(f"Failed to initialize Gemini Client: {e}. Falling back to deterministic mode.")
                    self._client = None
            else:
                logger.info("No GEMINI_API_KEY detected. AI operations will use grounded deterministic fallbacks.")
            self._initialized = True

        return self._client

    @property
    def is_available(self) -> bool:
        return self.get_client() is not None


gemini_manager = GeminiClientManager()
