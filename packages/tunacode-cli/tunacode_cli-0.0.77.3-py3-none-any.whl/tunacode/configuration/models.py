"""
Module: tunacode.configuration.models

Configuration data models and model registry for TunaCode CLI.
Defines available AI models and their configurations.
"""

from tunacode.types import ModelConfig, ModelName, ModelPricing
from tunacode.types import ModelRegistry as ModelRegistryType


class ModelRegistry:
    def __init__(self):
        self._models = self._load_default_models()

    def _load_default_models(self) -> ModelRegistryType:
        return {
            "anthropic:claude-opus-4-20250514": ModelConfig(
                pricing=ModelPricing(input=3.00, cached_input=1.50, output=15.00)
            ),
            "anthropic:claude-sonnet-4-20250514": ModelConfig(
                pricing=ModelPricing(input=3.00, cached_input=1.50, output=15.00)
            ),
            "anthropic:claude-3-7-sonnet-latest": ModelConfig(
                pricing=ModelPricing(input=3.00, cached_input=1.50, output=15.00)
            ),
            "google/gemini-2.5-flash-lite-preview-06-17": ModelConfig(
                pricing=ModelPricing(input=0.10, cached_input=0.025, output=0.40)
            ),
            "google-gla:gemini-2.0-flash": ModelConfig(
                pricing=ModelPricing(input=0.10, cached_input=0.025, output=0.40)
            ),
            "google-gla:gemini-2.5-flash-preview-05-20": ModelConfig(
                pricing=ModelPricing(input=0.15, cached_input=0.025, output=0.60)
            ),
            "google-gla:gemini-2.5-pro-preview-05-06": ModelConfig(
                pricing=ModelPricing(input=1.25, cached_input=0.025, output=10.00)
            ),
            "openai:gpt-4.1": ModelConfig(
                pricing=ModelPricing(input=2.00, cached_input=0.50, output=8.00)
            ),
            "openai:gpt-4.1-mini": ModelConfig(
                pricing=ModelPricing(input=0.40, cached_input=0.10, output=1.60)
            ),
            "openai:gpt-4.1-nano": ModelConfig(
                pricing=ModelPricing(input=0.10, cached_input=0.025, output=0.40)
            ),
            "openai:gpt-4o": ModelConfig(
                pricing=ModelPricing(input=2.50, cached_input=1.25, output=10.00)
            ),
            "openai:o3": ModelConfig(
                pricing=ModelPricing(input=10.00, cached_input=2.50, output=40.00)
            ),
            "openai:o3-mini": ModelConfig(
                pricing=ModelPricing(input=1.10, cached_input=0.55, output=4.40)
            ),
            "openrouter:mistralai/devstral-small": ModelConfig(
                pricing=ModelPricing(input=0.07, cached_input=0.035, output=0.10)
            ),
            "openrouter:codex-mini-latest": ModelConfig(
                pricing=ModelPricing(input=1.50, cached_input=0.75, output=6.00)
            ),
            "openrouter:o4-mini-high": ModelConfig(
                pricing=ModelPricing(input=1.10, cached_input=0.55, output=4.40)
            ),
            "openrouter:o3": ModelConfig(
                pricing=ModelPricing(input=10.00, cached_input=5.00, output=40.00)
            ),
            "openrouter:o4-mini": ModelConfig(
                pricing=ModelPricing(input=1.10, cached_input=0.55, output=4.40)
            ),
            "openrouter:openai/gpt-4.1": ModelConfig(
                pricing=ModelPricing(input=2.00, cached_input=1.00, output=8.00)
            ),
            "openrouter:openai/gpt-4.1-mini": ModelConfig(
                pricing=ModelPricing(input=0.40, cached_input=0.20, output=1.60)
            ),
            "openrouter:openai/gpt-4.1-nano": ModelConfig(
                pricing=ModelPricing(input=0.10, cached_input=0.05, output=0.40)
            ),
            "openrouter:google/gemini-2.5-flash-lite-preview-06-17": ModelConfig(
                pricing=ModelPricing(input=0.10, cached_input=0.025, output=0.40)
            ),
        }

    def get_model(self, name: ModelName) -> ModelConfig:
        return self._models.get(name)

    def list_models(self) -> ModelRegistryType:
        return self._models.copy()

    def list_model_ids(self) -> list[ModelName]:
        return list(self._models.keys())
