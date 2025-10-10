"""
Model Initialization Module.

This module provides the `Model` class for dynamically initializing and managing
Large Language Model (LLM) instances based on a specified provider. Supported providers
include OpenAI, Anthropic, Mistral, Fireworks, Google Generative AI, Grok and Groq.
"""

import os

# Standard library imports
from typing import Any, Optional, Self, Union

import boto3
import vertexai
from botocore.exceptions import ClientError
from langchain_anthropic import ChatAnthropic
from langchain_aws import ChatBedrock

# Third-party imports
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_fireworks import ChatFireworks
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_vertexai import ChatVertexAI
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_openai import ChatOpenAI
from langchain_xai import ChatXAI

# Internal application imports
from crypto_com_agent_client.config.constants import (
    BEDROCK_GUARDRAIL_VERSION_DEFAULT,
    BEDROCK_MODEL_DEFAULT,
    LLAMA4_MODEL,
    MODEL_DEFAULT,
    PROVIDER_DEFAULT,
)
from crypto_com_agent_client.lib.enums.provider_enum import Provider


class Model:
    """
    A class to handle dynamic initialization and management of Large Language Model (LLM) instances.

    This class supports multiple providers and ensures the correct model is initialized
    with appropriate configurations and API keys. It also supports optional tool binding
    for enhanced functionality.

    Supported providers:
        - OpenAI
        - Anthropic
        - Mistral
        - Fireworks
        - Google Generative AI
        - Grok
        - Groq
        - Vertex AI
        - Bedrock

    Attributes:
        provider (Provider): The specified provider for the model.
        api_key (str): The API key used for authentication with the provider.
        temeprature: The model temperature parameter.
        model (Optional[str]): The specific model name (optional). If not provided,
                               default models for the provider will be used.
        model_instance (Union[ChatOpenAI, ChatAnthropic, ChatMistralAI, ChatFireworks, ChatGoogleGenerativeAI, ChatXAI, ChatGroq, ChatVertexAI, ChatBedrock]):
            The initialized LLM instance.

    Example:
        >>> from lib.enums.model_enum import Provider
        >>> from core.model import Model
        >>>
        >>> model = Model(provider=Provider.OpenAI, api_key="your-api-key", model="gpt-4", temeprature=0)
        >>> print(model.model)
    """

    def __init__(
        self,
        api_key: str,
        temperature: int = 1,
        provider: Provider = PROVIDER_DEFAULT,
        model: Optional[str] = MODEL_DEFAULT,
        project_id: Optional[str] = None,
        location_id: Optional[str] = None,
        model_kwargs: Optional[dict] = None,
        knowledge_base_id: Optional[str] = None,
        guardrail_id: Optional[str] = None,
        guardrail_version: Optional[str] = None,
        min_relevance_score: Optional[float] = None,
        debug_logging: bool = False,
    ) -> None:
        """
        Initialize the Model instance.

        Args:
            provider (Provider): The provider enum (e.g., `Provider.OpenAI`, `Provider.Anthropic`).
            api_key (str): The API key for authenticating with the provider.
            model (Optional[str]): The specific model name (optional). If not provided,
                                   default models for the provider will be used.
            project_id (Optional[str]): The Google Cloud project ID (required for Vertex AI).
            location_id (Optional[str]): The Google Cloud location ID (required for Vertex AI).
            knowledge_base_id (Optional[str]): AWS Bedrock Knowledge Base ID (optional).
            guardrail_id (Optional[str]): AWS Bedrock Guardrail ID (optional).
            guardrail_version (Optional[str]): AWS Bedrock Guardrail version (optional).
            min_relevance_score (Optional[float]): Minimum relevance score (0.0-1.0) for KB results.

        Example:
            >>> from lib.enums.model_enum import Provider
            >>> model = Model(provider=Provider.OpenAI, api_key="your-api-key")
        """
        self.provider: Provider = provider
        self.api_key: str = api_key
        self.temperature: int = temperature
        self.model: str = model
        self.project_id: Optional[str] = project_id
        self.location_id: Optional[str] = location_id
        self.model_kwargs: Optional[dict] = model_kwargs
        self.knowledge_base_id: Optional[str] = knowledge_base_id
        self.guardrail_id: Optional[str] = guardrail_id
        self.guardrail_version: Optional[str] = guardrail_version
        self.min_relevance_score: Optional[float] = min_relevance_score
        self.debug_logging: bool = debug_logging
        self.bedrock_agent_runtime: Optional[Any] = None
        self.model_instance: Union[
            ChatOpenAI,
            ChatAnthropic,
            ChatMistralAI,
            ChatFireworks,
            ChatGoogleGenerativeAI,
            ChatXAI,
            ChatGroq,
            ChatVertexAI,
            ChatBedrock,
        ] = self.initialize_model()

    def initialize_model(self: Self) -> Union[
        ChatOpenAI,
        ChatAnthropic,
        ChatMistralAI,
        ChatFireworks,
        ChatGoogleGenerativeAI,
        ChatXAI,
        ChatGroq,
        ChatVertexAI,
        ChatBedrock,
    ]:
        """
        Dynamically initializes the model based on the provider and optional model name.

        This method validates the provider and returns a model instance with default
        or user-specified configurations.

        Returns:

            Union[ChatOpenAI, ChatAnthropic, ChatMistralAI, ChatFireworks, ChatGoogleGenerativeAI, ChatXAI, ChatGroq, ChatVertexAI, ChatBedrock]:
                An initialized LLM instance corresponding to the provider.

        Raises:
            ValueError: If the provider is unsupported or required configuration is missing.

        Example:
            >>> model = Model(provider=Provider.Anthropic, api_key="your-api-key")
            >>> model_instance = model.initialize_model()
        """
        if self.provider == Provider.OpenAI:
            return ChatOpenAI(
                model=self.model or "gpt-4",
                temperature=self.temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=self.api_key,
            )

        elif self.provider == Provider.Anthropic:
            return ChatAnthropic(
                model=self.model or "claude-3-5-sonnet-20240620",
                temperature=self.temperature,
                max_tokens=1024,
                timeout=None,
                max_retries=2,
                api_key=self.api_key,
            )

        elif self.provider == Provider.Mistral:
            return ChatMistralAI(
                model=self.model or "mistral-large-latest",
                temperature=self.temperature,
                max_retries=2,
                api_key=self.api_key,
            )

        elif self.provider == Provider.Fireworks:
            return ChatFireworks(
                model=self.model or "accounts/fireworks/models/llama-v3-70b-instruct",
                temperature=self.temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=self.api_key,
            )

        elif self.provider == Provider.GoogleGenAI:
            return ChatGoogleGenerativeAI(
                model=self.model or "gemini-1.5-pro",
                temperature=self.temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=self.api_key,
            )

        elif self.provider == Provider.Grok:
            return ChatXAI(
                model=self.model or "grok-3",
                xai_api_key=self.api_key,
                temperature=self.temperature,
            )

        elif self.provider == Provider.Groq:
            return ChatGroq(
                model=self.model or LLAMA4_MODEL,
                temperature=self.temperature,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                api_key=self.api_key,
            )
        elif self.provider == Provider.VertexAI:
            if not self.project_id or not self.location_id:
                raise ValueError(
                    "project_id and location_id are required for Vertex AI"
                )

            try:
                # Initialize Vertex AI
                vertexai.init(project=self.project_id, location=self.location_id)

                return ChatVertexAI(
                    model_name=self.model
                    or "publishers/google/models/gemini-2.0-flash-001",
                    project=self.project_id,
                    location=self.location_id,
                    temperature=self.temperature,
                    max_retries=2,
                )
            except Exception as e:
                raise ValueError(f"Failed to initialize Vertex AI: {str(e)}")

        elif self.provider == Provider.Bedrock:
            # AWS Bedrock configuration
            # Can use api_key as AWS access key ID, or rely on environment/default credentials
            aws_config = {}
            if self.api_key and self.api_key != "":
                # Parse api_key format: "ACCESS_KEY_ID:SECRET_ACCESS_KEY:REGION" or just use as access key
                parts = self.api_key.split(":")
                if len(parts) == 3:
                    aws_config["aws_access_key_id"] = parts[0]
                    aws_config["aws_secret_access_key"] = parts[1]
                    aws_config["region_name"] = parts[2]
                elif len(parts) == 2:
                    aws_config["aws_access_key_id"] = parts[0]
                    aws_config["aws_secret_access_key"] = parts[1]
                    aws_config["region_name"] = self.location_id or "us-east-1"
                else:
                    # Just use as access key ID, expect secret key from env
                    aws_config["aws_access_key_id"] = self.api_key
                    aws_config["region_name"] = self.location_id or "us-east-1"
            elif self.location_id:
                aws_config["region_name"] = self.location_id

            # Use model_kwargs from config or defaults
            model_kwargs = self.model_kwargs or {}

            # Always include temperature and max_tokens if not provided
            if "temperature" not in model_kwargs:
                model_kwargs["temperature"] = self.temperature
            if "max_tokens" not in model_kwargs:
                model_kwargs["max_tokens"] = 1024

            # Use configuration values for guardrail and knowledge base
            guardrail_id = self.guardrail_id
            guardrail_version = (
                self.guardrail_version or BEDROCK_GUARDRAIL_VERSION_DEFAULT
            )
            knowledge_base_id = self.knowledge_base_id

            # Prepare ChatBedrock parameters
            bedrock_params = {
                "model_id": self.model or BEDROCK_MODEL_DEFAULT,
                "model_kwargs": model_kwargs,
                **aws_config,
            }

            # Add guardrail configuration if provided
            if guardrail_id:
                bedrock_params["guardrails"] = {
                    "guardrailIdentifier": guardrail_id,
                    "guardrailVersion": guardrail_version,
                    "trace": True,  # Enable trace for debugging
                }
                if self.debug_logging:
                    print(
                        f"Using guardrail: {guardrail_id} (version: {guardrail_version})"
                    )

            # Initialize Bedrock Agent Runtime for knowledge base if needed
            if knowledge_base_id:
                try:
                    # Extract AWS credentials from aws_config or use defaults
                    runtime_config = {}
                    if "region_name" in aws_config:
                        runtime_config["region_name"] = aws_config["region_name"]
                    if "aws_access_key_id" in aws_config:
                        runtime_config["aws_access_key_id"] = aws_config[
                            "aws_access_key_id"
                        ]
                    if "aws_secret_access_key" in aws_config:
                        runtime_config["aws_secret_access_key"] = aws_config[
                            "aws_secret_access_key"
                        ]

                    self.bedrock_agent_runtime = boto3.client(
                        "bedrock-agent-runtime", **runtime_config
                    )
                    if self.debug_logging:
                        print(f"Using knowledge base: {knowledge_base_id}")
                except Exception as e:
                    if self.debug_logging:
                        print(
                            f"Warning: Could not initialize knowledge base client: {e}"
                        )
                        print("Knowledge base features will be disabled.")
                    self.bedrock_agent_runtime = None

            return ChatBedrock(**bedrock_params)

        else:
            raise ValueError(f"Unsupported provider: {self.provider.value}")

    def query_knowledge_base(
        self,
        query: str,
        max_results: int = 5,
        min_relevance_score: Optional[float] = None,
    ) -> Optional[str]:
        """
        Query the AWS Bedrock Knowledge Base with optional score filtering.

        Args:
            query (str): The query to search for in the knowledge base.
            max_results (int): Maximum number of results to return.
            min_relevance_score (Optional[float]): Minimum score threshold for results.
                If not provided, uses the configured value or default.

        Returns:
            Optional[str]: The knowledge base results or None if unavailable.
        """
        if not self.bedrock_agent_runtime:
            return None

        knowledge_base_id = self.knowledge_base_id
        if not knowledge_base_id:
            return None

        # Use the provided threshold, or fall back to configured value, or default
        from crypto_com_agent_client.config.constants import MIN_RELEVANCE_SCORE

        # Properly handle None values - use first non-None value or default
        if min_relevance_score is not None:
            score_threshold = min_relevance_score
        elif (
            hasattr(self, "min_relevance_score")
            and self.min_relevance_score is not None
        ):
            score_threshold = self.min_relevance_score
        else:
            score_threshold = MIN_RELEVANCE_SCORE

        try:
            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=knowledge_base_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {"numberOfResults": max_results}
                },
            )

            if response and "retrievalResults" in response:
                results = []
                filtered_count = 0
                total_count = 0

                for result in response["retrievalResults"]:
                    total_count += 1
                    content = result.get("content", {}).get(
                        "text", "No content available"
                    )
                    score = result.get("score", 0)

                    # Only include results that meet the relevance threshold
                    if score >= score_threshold:
                        results.append(
                            f"\n[Result {len(results) + 1}] (Score: {score:.3f})\n{content}"
                        )
                    else:
                        filtered_count += 1
                        if self.debug_logging:
                            print(
                                f"   ⚠️ Filtered out result with low score: {score:.3f} < {score_threshold}"
                            )

                if self.debug_logging and filtered_count > 0:
                    print(
                        f"   📊 Filtered {filtered_count}/{total_count} results below threshold ({score_threshold})"
                    )

                if results:
                    return "\n".join(results)
                else:
                    if self.debug_logging:
                        print(
                            f"   ❌ All {total_count} results were below threshold ({score_threshold})"
                        )
                    return "No relevant information found in the knowledge base."
            else:
                return "No results found in the knowledge base."

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            error_message = e.response.get("Error", {}).get("Message", "")
            return f"Knowledge base query failed: {error_code} - {error_message}"
        except Exception as e:
            return f"Knowledge base query error: {str(e)}"

    def bind_tools(self: Self, tools: Any) -> Runnable[LanguageModelInput, BaseMessage]:
        """
        Binds additional tools to the model if supported by the provider.

        Certain models support integrating tools (e.g., for enhanced functionality).
        This method checks if the model instance supports tool binding and performs
        the operation. If not supported, it raises a `NotImplementedError`.

        Args:
            tools (Any): A collection of tools to bind to the model.

        Returns:
            Runnable[LanguageModelInput, BaseMessage]: The result of the tool binding operation if supported.

        Raises:
            NotImplementedError: If the model does not support tool binding.

        Example:
            >>> from langchain_core.tools import BaseTool
            >>> model = Model(provider=Provider.OpenAI, api_key="your-api-key")
            >>> bound_model = model.bind_tools([some_tool])
        """
        if hasattr(self.model_instance, "bind_tools"):
            return self.model_instance.bind_tools(tools)
        raise NotImplementedError(
            f"Tool binding not supported for {self.provider.value}."
        )
