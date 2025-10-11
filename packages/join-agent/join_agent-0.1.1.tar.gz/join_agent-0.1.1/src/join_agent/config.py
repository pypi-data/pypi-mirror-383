"""
Configuration for the Join Agent.
"""

import os

from pydantic import Field
from pydantic_settings import BaseSettings


class JoinAgentConfig(BaseSettings):
    """Configuration settings for the feature creation Agent."""

    # AI Provider Configuration
    ai_provider: str = Field(
        default=os.getenv("LLM_PROVIDER", "openai"),
        env="LLM_PROVIDER",
        description="AI provider to use (e.g., openai, anthropic, etc.)",
    )
    ai_task_type: str = Field(
        default="join_suggestion", description="Task type for AI requests"
    )
    model_name: str = Field(
        default=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        env="LLM_MODEL",
        description="AI model to use (e.g., gpt-4, claude-2, etc.)",
    )
    temperature: float = Field(
        default=0.1, ge=0.0, le=2.0, description="AI model temperature"
    )
    max_tokens: int = Field(
        default=5000, ge=100, le=8000, description="Maximum tokens for AI response"
    )
    api_key: str = Field(
        default=os.getenv("LLM_API_KEY", ""),
        env="LLM_API_KEY",
        description="API key for the LLM provider",
    )
