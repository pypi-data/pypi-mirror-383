from typing import Any, ClassVar

from pydantic import Field, field_validator, model_validator

from memos.configs.base import BaseConfig


class BaseLLMConfig(BaseConfig):
    """Base configuration class for LLMs."""

    model_name_or_path: str = Field(..., description="Model name or path")
    temperature: float = Field(default=0.8, description="Temperature for sampling")
    max_tokens: int = Field(default=1024, description="Maximum number of tokens to generate")
    top_p: float = Field(default=0.9, description="Top-p sampling parameter")
    top_k: int = Field(default=50, description="Top-k sampling parameter")
    remove_think_prefix: bool = Field(
        default=False,
        description="Remove content within think tags from the generated text",
    )


class OpenAILLMConfig(BaseLLMConfig):
    api_key: str = Field(..., description="API key for OpenAI")
    api_base: str = Field(
        default="https://api.openai.com/v1", description="Base URL for OpenAI API"
    )
    extra_body: Any = Field(default=None, description="extra body")


class QwenLLMConfig(BaseLLMConfig):
    api_key: str = Field(..., description="API key for DashScope (Qwen)")
    api_base: str = Field(
        default="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        description="Base URL for Qwen OpenAI-compatible API",
    )
    extra_body: Any = Field(default=None, description="extra body")
    model_name_or_path: str = Field(..., description="Model name for Qwen, e.g., 'qwen-plus'")


class DeepSeekLLMConfig(BaseLLMConfig):
    api_key: str = Field(..., description="API key for DeepSeek")
    api_base: str = Field(
        default="https://api.deepseek.com",
        description="Base URL for DeepSeek OpenAI-compatible API",
    )
    extra_body: Any = Field(default=None, description="Extra options for API")
    model_name_or_path: str = Field(
        ..., description="Model name: 'deepseek-chat' or 'deepseek-reasoner'"
    )


class AzureLLMConfig(BaseLLMConfig):
    base_url: str = Field(
        default="https://api.openai.azure.com/",
        description="Base URL for Azure OpenAI API",
    )
    api_version: str = Field(
        default="2024-03-01-preview",
        description="API version for Azure OpenAI",
    )
    api_key: str = Field(..., description="API key for Azure OpenAI")


class OllamaLLMConfig(BaseLLMConfig):
    api_base: str = Field(
        default="http://localhost:11434",
        description="Base URL for Ollama API",
    )


class HFLLMConfig(BaseLLMConfig):
    do_sample: bool = Field(
        default=False,
        description="Whether to use sampling (if False, always greedy/argmax decoding)",
    )
    add_generation_prompt: bool = Field(
        default=True,
        description="Apply generation template for the conversation",
    )


class VLLMLLMConfig(BaseLLMConfig):
    api_key: str = Field(default="", description="API key for vLLM (optional for local server)")
    api_base: str = Field(
        default="http://localhost:8088/v1",
        description="Base URL for vLLM API",
    )


class LLMConfigFactory(BaseConfig):
    """Factory class for creating LLM configurations."""

    backend: str = Field(..., description="Backend for LLM")
    config: dict[str, Any] = Field(..., description="Configuration for the LLM backend")

    backend_to_class: ClassVar[dict[str, Any]] = {
        "openai": OpenAILLMConfig,
        "ollama": OllamaLLMConfig,
        "azure": AzureLLMConfig,
        "huggingface": HFLLMConfig,
        "vllm": VLLMLLMConfig,
        "huggingface_singleton": HFLLMConfig,  # Add singleton support
        "qwen": QwenLLMConfig,
        "deepseek": DeepSeekLLMConfig,
    }

    @field_validator("backend")
    @classmethod
    def validate_backend(cls, backend: str) -> str:
        """Validate the backend field."""
        if backend not in cls.backend_to_class:
            raise ValueError(f"Invalid backend: {backend}")
        return backend

    @model_validator(mode="after")
    def create_config(self) -> "LLMConfigFactory":
        config_class = self.backend_to_class[self.backend]
        self.config = config_class(**self.config)
        return self
