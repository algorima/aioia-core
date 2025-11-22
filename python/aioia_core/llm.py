"""
LLM infrastructure for AIoIA projects.

Provides LLM provider abstractions and model settings.
"""

from __future__ import annotations

from typing import Any, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


# ==============================================================================
# Model Settings
# ==============================================================================


class ModelSettings(BaseModel):
    """Settings required for initializing a chat model."""

    chat_model: str = Field(description="The chat model name")
    temperature: float = Field(default=0.0, description="The temperature for the chat model")
    seed: Optional[int] = Field(default=None, description="The random seed for the chat model")


# ==============================================================================
# LLM Provider System
# ==============================================================================


class BaseProvider:
    """Base class for LLM providers."""

    def init_chat_model(
        self,
        model_settings: ModelSettings,
        api_key: str,
        response_format: dict[str, Any] | None = None,
    ) -> BaseChatModel:
        """Initialize chat model with settings."""
        raise NotImplementedError


class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation."""

    def init_chat_model(
        self,
        model_settings: ModelSettings,
        api_key: str,
        response_format: dict[str, Any] | None = None,
    ) -> BaseChatModel:
        """Initialize OpenAI chat model."""
        kwargs: dict[str, Any] = {
            "model": model_settings.chat_model,
            "temperature": model_settings.temperature,
            "api_key": api_key,
        }

        if model_settings.seed is not None:
            kwargs["seed"] = model_settings.seed

        if response_format:
            kwargs["model_kwargs"] = {"response_format": response_format}

        return ChatOpenAI(**kwargs)


class AnthropicProvider(BaseProvider):
    """Anthropic provider implementation."""

    def init_chat_model(
        self,
        model_settings: ModelSettings,
        api_key: str,
        response_format: dict[str, Any] | None = None,
    ) -> BaseChatModel:
        """Initialize Anthropic chat model."""
        return ChatAnthropic(
            model=model_settings.chat_model,
            temperature=model_settings.temperature,
            api_key=api_key,
        )


class ProviderRegistry:
    """Registry for LLM providers."""

    def __init__(self):
        self._providers: dict[str, BaseProvider] = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
        }

    def get_provider(self, provider_name: str) -> BaseProvider:
        """Get provider by name."""
        if provider_name not in self._providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return self._providers[provider_name]
