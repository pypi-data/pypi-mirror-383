"""Configuration models for OpenAgents agents."""

import os
import yaml
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from openagents.config.llm_configs import MODEL_CONFIGS, LLMProviderType
from openagents.config.prompt_templates import (
    DEFAULT_LLM_USER_PROMPT_TEMPLATE,
    DEFAULT_SYSTEM_PROMPT_TEMPLATE,
    DEFAULT_AGENT_USER_PROMPT_TEMPLATE,
)
from openagents.models.mcp_config import MCPServerConfig


class AgentTriggerConfigItem(BaseModel):
    """Trigger for an agent."""

    event: str = Field(..., description="Event name to trigger the agent")
    instruction: Optional[str] = Field(
        default=None, description="Instruction on how to respond to the event"
    )



class AgentConfig(BaseModel):
    """Configuration for a SimpleAgentRunner instance.

    This class represents all configuration parameters needed to initialize
    a SimpleAgentRunner, including model settings, network protocols, and
    provider-specific options.

    Example:
        config = AgentConfig(
            model_name="gpt-4o-mini",
            instruction="You are a helpful assistant.",
            provider="openai"
        )

        # Load from YAML
        config = AgentConfig.from_yaml("config.yaml")
    """

    model_config = ConfigDict(
        use_enum_values=True, extra="allow"  # Allow provider-specific kwargs
    )
    

    # Core agent configuration
    instruction: str = Field(..., description="System instruction/prompt for the agent")
    model_name: str = Field(..., description="Name of the model to use")

    # Provider configuration
    provider: Optional[LLMProviderType] = Field(
        None, description="Model provider (auto-detected if not specified)"
    )
    api_base: Optional[str] = Field(
        None, description="Custom API base URL (overrides provider defaults)"
    )
    api_key: Optional[str] = Field(
        None, description="API key (if not provided, will use environment variables)"
    )

    # Triggers
    triggers: List[AgentTriggerConfigItem] = Field(
        default_factory=list, description="Triggers for the agent"
    )

    # React to all messages
    react_to_all_messages: bool = Field(
        default=False, description="Whether to react to all messages"
    )

    # Maximum iterations
    max_iterations: int = Field(
        default=10,
        description="Maximum number of iterations for the agent to respond to the context",
    )

    # Prompt templates
    system_prompt_template: Optional[str] = Field(
        default=DEFAULT_SYSTEM_PROMPT_TEMPLATE,
        description="Custom system prompt template (uses instruction if not provided)",
    )
    user_prompt_template: str = Field(
        default=DEFAULT_AGENT_USER_PROMPT_TEMPLATE,
        description="Custom user prompt template for conversation formatting (uses default if not provided)",
    )
    llm_user_prompt_template: Optional[str] = Field(
        default=DEFAULT_LLM_USER_PROMPT_TEMPLATE,
        description="Custom user prompt template for LLM conversation formatting (uses default if not provided)",
    )

    # MCP (Model Context Protocol) servers
    mcps: List[MCPServerConfig] = Field(
        default_factory=list,
        description="List of MCP servers to connect to for additional tools and capabilities"
    )

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v):
        """Validate model name is non-empty string."""
        if not v or not isinstance(v, str):
            raise ValueError("Model name must be a non-empty string")
        return v

    @field_validator("api_base")
    @classmethod
    def validate_api_base(cls, v):
        """Validate API base URL format."""
        if v is not None:
            if not isinstance(v, str) or not (
                v.startswith("http://") or v.startswith("https://")
            ):
                raise ValueError("API base must be a valid HTTP/HTTPS URL")
        return v

    @field_validator("system_prompt_template")
    @classmethod
    def validate_system_prompt_template(cls, v):
        """Validate system prompt template format."""
        if v is not None and (not isinstance(v, str) or not v.strip()):
            raise ValueError("System prompt template must be a non-empty string")
        return v

    @field_validator("user_prompt_template")
    @classmethod
    def validate_user_prompt_template(cls, v):
        """Validate user prompt template format."""
        if v is not None and (not isinstance(v, str) or not v.strip()):
            raise ValueError("User prompt template must be a non-empty string")
        return v

    def determine_provider(self) -> str:
        """Determine the model provider based on configuration.

        Uses the same logic as SimpleAgentRunner._determine_provider().

        Returns:
            str: The determined provider name
        """
        if self.provider:
            return self.provider.lower()

        # Auto-detect provider based on API base
        if self.api_base:
            if "azure.com" in self.api_base:
                return "azure"
            elif "deepseek.com" in self.api_base:
                return "deepseek"
            elif "aliyuncs.com" in self.api_base:
                return "qwen"
            elif "x.ai" in self.api_base:
                return "grok"
            elif "anthropic.com" in self.api_base:
                return "claude"
            elif "googleapis.com" in self.api_base:
                return "gemini"

        # Auto-detect based on model name
        model_lower = self.model_name.lower()
        if any(name in model_lower for name in ["gpt", "openai"]):
            return "openai"
        elif any(name in model_lower for name in ["claude"]):
            return "claude"
        elif any(name in model_lower for name in ["gemini"]):
            return "gemini"
        elif any(name in model_lower for name in ["deepseek"]):
            return "deepseek"
        elif any(name in model_lower for name in ["qwen"]):
            return "qwen"
        elif any(name in model_lower for name in ["grok"]):
            return "grok"
        elif any(name in model_lower for name in ["mistral", "mixtral"]):
            return "mistral"
        elif any(name in model_lower for name in ["command"]):
            return "cohere"
        elif "llama" in model_lower or "meta-" in model_lower:
            return "together"
        elif "sonar" in model_lower:
            return "perplexity"
        elif "anthropic." in self.model_name:
            return "bedrock"

        # Default to OpenAI
        return "openai"

    def get_supported_models(self, provider: Optional[str] = None) -> List[str]:
        """Get list of supported models for a provider.

        Args:
            provider: Provider name (uses auto-detected if not specified)

        Returns:
            List of supported model names
        """
        provider = provider or self.determine_provider()
        config = MODEL_CONFIGS.get(provider, {})
        return config.get("models", [])

    def get_default_api_base(self, provider: Optional[str] = None) -> Optional[str]:
        """Get default API base URL for a provider.

        Args:
            provider: Provider name (uses auto-detected if not specified)

        Returns:
            Default API base URL or None
        """
        provider = provider or self.determine_provider()
        config = MODEL_CONFIGS.get(provider, {})
        return config.get("api_base")

    def get_effective_system_prompt_template(self) -> str:
        """Get the effective system prompt template (custom or instruction).

        Returns:
            System prompt template to use
        """
        return self.system_prompt_template or self.instruction

    @classmethod
    def from_yaml(cls, file_path: str) -> "AgentConfig":
        """Load configuration from a YAML file.

        Args:
            file_path: Path to the YAML configuration file

        Returns:
            AgentConfig instance

        Raises:
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is invalid
            ValueError: If configuration is invalid
        """
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        # Extract config section if present (matches example YAML structure)
        if "config" in data:
            config_data = data["config"]
        else:
            config_data = data

        return cls(**config_data)

    def to_yaml(self, file_path: str, include_type: bool = True) -> None:
        """Save configuration to a YAML file.

        Args:
            file_path: Path where to save the YAML file
            include_type: Whether to include the 'type: simple' field
        """
        config_dict = self.model_dump(exclude_none=True)

        if include_type:
            output = {"type": "simple", "config": config_dict}
        else:
            output = config_dict

        with open(file_path, "w") as f:
            yaml.dump(output, f, default_flow_style=False, sort_keys=False)


# Factory functions for common configurations


def create_openai_config(
    model_name: str = "gpt-4o-mini",
    instruction: str = "You are a helpful AI assistant.",
    api_key: Optional[str] = None,
    system_prompt_template: Optional[str] = None,
    user_prompt_template: Optional[str] = None,
) -> AgentConfig:
    """Create a configuration for OpenAI models.

    Args:
        model_name: OpenAI model name
        instruction: System instruction for the agent
        api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        system_prompt_template: Custom system prompt template
        user_prompt_template: Custom user prompt template

    Returns:
        AgentConfig configured for OpenAI
    """
    config_kwargs = {
        "model_name": model_name,
        "instruction": instruction,
        "provider": LLMProviderType.OPENAI,
        "api_key": api_key or os.getenv("OPENAI_API_KEY"),
    }

    if system_prompt_template is not None:
        config_kwargs["system_prompt_template"] = system_prompt_template
    if user_prompt_template is not None:
        config_kwargs["user_prompt_template"] = user_prompt_template

    return AgentConfig(**config_kwargs)


def create_claude_config(
    model_name: str = "claude-3-5-sonnet-20241022",
    instruction: str = "You are Claude, an AI assistant by Anthropic.",
    api_key: Optional[str] = None,
    system_prompt_template: Optional[str] = None,
    user_prompt_template: Optional[str] = None,
) -> AgentConfig:
    """Create a configuration for Anthropic Claude models.

    Args:
        model_name: Claude model name
        instruction: System instruction for the agent
        api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
        system_prompt_template: Custom system prompt template
        user_prompt_template: Custom user prompt template

    Returns:
        AgentConfig configured for Claude
    """
    config_kwargs = {
        "model_name": model_name,
        "instruction": instruction,
        "provider": LLMProviderType.CLAUDE,
        "api_key": api_key or os.getenv("ANTHROPIC_API_KEY"),
    }

    if system_prompt_template is not None:
        config_kwargs["system_prompt_template"] = system_prompt_template
    if user_prompt_template is not None:
        config_kwargs["user_prompt_template"] = user_prompt_template

    return AgentConfig(**config_kwargs)


def create_gemini_config(
    model_name: str = "gemini-1.5-pro",
    instruction: str = "You are a helpful AI assistant powered by Google's Gemini.",
    api_key: Optional[str] = None,
    system_prompt_template: Optional[str] = None,
    user_prompt_template: Optional[str] = None,
) -> AgentConfig:
    """Create a configuration for Google Gemini models.

    Args:
        model_name: Gemini model name
        instruction: System instruction for the agent
        api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)
        system_prompt_template: Custom system prompt template
        user_prompt_template: Custom user prompt template

    Returns:
        AgentConfig configured for Gemini
    """
    config_kwargs = {
        "model_name": model_name,
        "instruction": instruction,
        "provider": LLMProviderType.GEMINI,
        "api_key": api_key or os.getenv("GOOGLE_API_KEY"),
    }

    if system_prompt_template is not None:
        config_kwargs["system_prompt_template"] = system_prompt_template
    if user_prompt_template is not None:
        config_kwargs["user_prompt_template"] = user_prompt_template

    return AgentConfig(**config_kwargs)


def create_deepseek_config(
    model_name: str = "deepseek-chat",
    instruction: str = "You are a helpful AI assistant powered by DeepSeek.",
    api_key: Optional[str] = None,
    system_prompt_template: Optional[str] = None,
    user_prompt_template: Optional[str] = None,
) -> AgentConfig:
    """Create a configuration for DeepSeek models.

    Args:
        model_name: DeepSeek model name
        instruction: System instruction for the agent
        api_key: DeepSeek API key (uses OPENAI_API_KEY env var if not provided)
        system_prompt_template: Custom system prompt template
        user_prompt_template: Custom user prompt template

    Returns:
        AgentConfig configured for DeepSeek
    """
    config_kwargs = {
        "model_name": model_name,
        "instruction": instruction,
        "provider": LLMProviderType.DEEPSEEK,
        "api_key": api_key
        or os.getenv("OPENAI_API_KEY"),  # DeepSeek uses OpenAI-compatible format
    }

    if system_prompt_template is not None:
        config_kwargs["system_prompt_template"] = system_prompt_template
    if user_prompt_template is not None:
        config_kwargs["user_prompt_template"] = user_prompt_template

    return AgentConfig(**config_kwargs)
