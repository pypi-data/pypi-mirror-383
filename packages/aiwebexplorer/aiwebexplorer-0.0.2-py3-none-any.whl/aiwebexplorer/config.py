from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Environment types."""

    DEV = "DEV"
    TEST = "TEST"
    CI = "CI"
    PROD = "PROD"


class Config(BaseSettings):
    """Application settings."""

    ENV: Environment = Environment.DEV
    LOG_LEVEL: str = "INFO"  # Allowed: DEBUG, INFO, WARNING, ERROR, CRITICAL

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


# Export a ready-to-use settings object
config = Config()
