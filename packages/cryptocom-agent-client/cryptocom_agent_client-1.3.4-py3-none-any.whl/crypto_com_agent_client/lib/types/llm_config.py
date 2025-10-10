"""
LLM Config Module.

This module defines the `LLMConfig` TypedDict, which represents the configuration
for Language Model (LLM) providers. It ensures type safety and clarity when passing
LLM-related parameters to the agent.
"""

# Standard library imports
from typing import Optional

# Third-party imports
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """
    TypedDict for Language Model (LLM) configuration.

    Attributes:
        provider (str): The name of the LLM provider (e.g., "OpenAI", "VertexAI", "Bedrock").
        model (Optional[str]): The specific model to use (e.g., "gpt-4").
            Defaults to the provider's default model if not provided.
        temperature (Optional[str]): The model temperature parameter.
        provider_api_key (Optional[str]): The API key for the provider. Required for all providers except Vertex AI and Bedrock (which can use default cloud authentication).
        project_id (Optional[str]): The Google Cloud project ID (required for Vertex AI).
        location_id (Optional[str]): The Google Cloud location ID (required for Vertex AI) or AWS region (for Bedrock).
        debug_logging (Optional[bool]): Enable/disable debug logging for model interactions and token usage.
        knowledge_base_id (Optional[str]): AWS Bedrock Knowledge Base ID (optional, Bedrock only).
        guardrail_id (Optional[str]): AWS Bedrock Guardrail ID (optional, Bedrock only).
        guardrail_version (Optional[str]): AWS Bedrock Guardrail version (optional, Bedrock only).
        min_relevance_score (Optional[float]): Minimum relevance score (0.0-1.0) for KB results. Defaults to 0.4.

    Example:
        >>> from lib.types.llm_config import LLMConfig
        >>> llm_config: LLMConfig = {
        ...     "provider": "OpenAI",
        ...     "model": "gpt-5-nano",
        ...     "temperature": 0,
        ...     "provider_api_key": "your-api-key",
        ...     "debug_logging": True
        ... }

        # For Vertex AI:
        >>> vertex_config: LLMConfig = {
        ...     "provider": "VertexAI",
        ...     "model": "publishers/meta/models/llama-4-maverick-17b-128e-instruct-maas",
        ...     "temperature": 0.7,
        ...     "project_id": "your-project-id",
        ...     "location_id": "us-east5",
        ...     "debug_logging": False
        ... }
    """

    provider: Optional[str] = Field(default="OpenAI")
    model: Optional[str] = Field(default="gpt-5-nano")
    temperature: Optional[float] = Field(default=1)
    provider_api_key: Optional[str] = Field(default=None, alias="provider-api-key")
    project_id: Optional[str] = Field(default=None, alias="project-id")
    location_id: Optional[str] = Field(default=None, alias="location-id")
    debug_logging: Optional[bool] = Field(default=False, alias="debug-logging")
    optimise_token_usage: Optional[bool] = Field(
        default=False, alias="optimise-token-usage"
    )
    model_kwargs: Optional[dict] = Field(default=None, alias="model-kwargs")
    knowledge_base_id: Optional[str] = Field(default=None, alias="knowledge-base-id")
    guardrail_id: Optional[str] = Field(default=None, alias="guardrail-id")
    guardrail_version: Optional[str] = Field(default=None, alias="guardrail-version")
    min_relevance_score: Optional[float] = Field(
        default=None, alias="min-relevance-score"
    )
