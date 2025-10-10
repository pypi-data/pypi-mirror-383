"""
Service Configuration Module.

This module handles the configuration and environment variable loading required for the application.
It sets up constants such as the default AI service provider, the default AI model, and the API client
key for interacting with Crypto.com services.

Constants:
    PROVIDER_DEFAULT (Provider): The default provider for AI services, set to OpenAI.
    MODEL_DEFAULT (str): The default model for AI operations, set to GPT-4.
    LLAMA4_MODEL (str): The default Llama 4 model for Groq provider.
    VERTEXAI_LOCATION_DEFAULT (str): The default location for Vertex AI operations.
"""

# Third-party imports
from dotenv import load_dotenv

# Internal application imports
from crypto_com_agent_client.lib.enums.provider_enum import Provider

# Load environment variables from a .env file
load_dotenv()


PROVIDER_DEFAULT = Provider.OpenAI
"""
The default provider for AI services.

This constant defines the default provider for AI services in the application. By default,
it is set to OpenAI. This value can be overridden by specifying a different provider during
initialization.

Example:
    >>> from lib.enums.model_enum import Provider
    >>> print(PROVIDER_DEFAULT)
    OpenAI
"""

MODEL_DEFAULT = "gpt-4"
"""
The default model to be used for AI operations.

This constant specifies the default AI model to be used in the application. It is set to GPT-4
for the OpenAI provider. This value can be overridden by specifying a different model during
initialization.

Example:
    >>> print(MODEL_DEFAULT)
    gpt-4
"""

LLAMA4_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"

VERTEXAI_LOCATION_DEFAULT = "us-west1"

BEDROCK_MODEL_DEFAULT = "anthropic.claude-3-haiku-20240307-v1:0"
"""
The default model for AWS Bedrock.

This constant specifies the default AI model to be used with AWS Bedrock provider.
It is set to Claude 3 Haiku by default. This value can be overridden by specifying
a different model during initialization.

Example:
    >>> print(BEDROCK_MODEL_DEFAULT)
    anthropic.claude-3-haiku-20240307-v1:0
"""

BEDROCK_GUARDRAIL_VERSION_DEFAULT = "DRAFT"
"""
The default guardrail version for AWS Bedrock.

This constant defines the default version to use when a guardrail ID is provided
but no specific version is specified. "DRAFT" uses the working draft version.

Example:
    >>> print(BEDROCK_GUARDRAIL_VERSION_DEFAULT)
    DRAFT
"""

MIN_RELEVANCE_SCORE = 0.4
"""
The minimum relevance score threshold for AWS Bedrock Knowledge Base results.

This constant defines the minimum score (0.0 to 1.0) that a knowledge base result
must have to be included in the context sent to the LLM. Results with scores below
this threshold are filtered out to prevent irrelevant information from being included.

A score of 0.4 means only results with 40% or higher relevance will be used.

Example:
    - Score 0.5: ✅ Included (above threshold)
    - Score 0.3: ❌ Filtered out (below threshold)
"""
DEFAULT_SYSTEM_INSTRUCTION = """You are an AI assistant specialized in blockchain and cryptocurrency operations, powered by Crypto.com's developer platform. You are helpful, accurate, and secure.

Key capabilities:
- Knowledge base: When relevant information is provided from the knowledge base, use it to provide accurate answers
- Blockchain/crypto operations: Use tool_dispatcher for wallet operations, balances, transactions, token management
- Tool listing: When asked about capabilities, use tool_dispatcher with list_tools function
- Combined responses: You can combine knowledge base information with function calls to provide comprehensive answers
- Custom queries: Use the appropriate tool for the query

Always prioritize user security and provide clear warnings for sensitive operations like private keys or transactions."""
"""
The default system instruction for the AI agent.

This constant defines the immutable default system instruction that provides the core
identity and capabilities of the AI agent. It establishes the agent as a blockchain and
cryptocurrency specialist powered by Crypto.com's developer platform.

The instruction covers:
- Core identity as a helpful, accurate, and secure AI assistant
- Key capabilities including blockchain operations and general queries
- Security guidelines for sensitive operations

This instruction serves as the foundation that can be extended with personality settings
and user-specific instructions without compromising the core system behavior.
"""
