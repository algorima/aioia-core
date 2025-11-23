"""Settings classes for AIoIA projects."""

from pydantic_settings import BaseSettings


class OpenAIAPISettings(BaseSettings):
    """
    OpenAI API authentication settings.

    Environment variables:
        OPENAI_API_KEY: OpenAI API key
    """

    api_key: str

    class Config:
        env_prefix = "OPENAI_"


class JWTSettings(BaseSettings):
    """
    JWT authentication settings.

    Environment variables:
        JWT_SECRET_KEY: Secret key for JWT signing and verification
    """

    secret_key: str

    class Config:
        env_prefix = "JWT_"
