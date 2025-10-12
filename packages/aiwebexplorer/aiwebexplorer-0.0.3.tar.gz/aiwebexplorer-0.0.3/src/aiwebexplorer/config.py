from enum import StrEnum
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Environment types."""

    DEV = "DEV"
    TEST = "TEST"
    CI = "CI"
    PROD = "PROD"


class Config(BaseSettings):
    """Application settings."""

    AWE_ENV: Environment = Environment.DEV
    AWE_LOG_LEVEL: str = "INFO"  # Allowed: DEBUG, INFO, WARNING, ERROR, CRITICAL
    AWE_LLM_PROVIDER: Literal["openai", "togetherai", "deepseek"] | None = None
    AWE_LLM_MODEL: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


# Export a ready-to-use settings object
config = Config()
