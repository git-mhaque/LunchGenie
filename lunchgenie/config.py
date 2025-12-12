"""
LunchGenie configuration and secrets loading.
Loads from .env (or environment), validates presence of secrets, and centralizes config access.

Usage:
    from lunchgenie.config import Config

    cfg = Config()
    print(cfg.openai_api_key)  # Do NOT print secrets in prod!
"""
import os
from dotenv import load_dotenv

class ConfigError(Exception):
    pass

class Config:
    def __init__(self, env_path: str = ".env"):
        # Load environment variables from .env (if exists)
        load_dotenv(dotenv_path=env_path, override=True)

        # Required
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ConfigError("Missing required OPENAI_API_KEY in environment or .env")

        # Optional service keys
        self.yelp_api_key = os.getenv("YELP_API_KEY")
        self.google_places_api_key = os.getenv("GOOGLE_PLACES_API_KEY")

        # Geolocation defaults
        self.default_latitude = os.getenv("DEFAULT_LATITUDE")
        self.default_longitude = os.getenv("DEFAULT_LONGITUDE")

        # Restaurant provider selection: 'yelp' or 'google'
        self.restaurant_provider = os.getenv("RESTAURANT_PROVIDER", "yelp").strip().lower()

        # Application environment (default: development)
        self.app_env = os.getenv("APP_ENV", "development")

    def summary(self) -> str:
        """Returns a non-sensitive config summary (for debugging only, skips secrets)"""
        return (
            f"Config("
            f"app_env={self.app_env}, "
            f"Yelp API={'set' if self.yelp_api_key else 'unset'}, "
            f"Google Places API={'set' if self.google_places_api_key else 'unset'}, "
            f"default_lat={self.default_latitude}, "
            f"default_lng={self.default_longitude})"
        )
