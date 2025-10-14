from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable

from langchain.schema import BaseMessage

from llm.direction import TokenDirection
from llm.types import LLMClientClass, LLMClientInstance


@dataclass
class ModelConfig:
    """Конфигурация для конкретной модели"""

    client_class: LLMClientClass
    token_counter: Callable[[list[BaseMessage], str, LLMClientInstance], int]
    pricing: dict[TokenDirection, float]
    moderation: Callable[[list[BaseMessage], LLMClientInstance], None] | None = None
    test_connection: Callable[[LLMClientInstance], bool | None] | None = None


class BaseProvider(ABC):
    """Базовый класс для провайдеров LLM
    Реестр моделей

    - Цены OpenAI: https://platform.openai.com/docs/pricing
    - Цены Gigachat: https://developers.sber.ru/docs/ru/gigachat/tariffs/legal-tariffs
    - Цены Anthropic: https://docs.anthropic.com/en/docs/about-claude/pricing
        - имена моделей https://docs.anthropic.com/en/docs/about-claude/models/overview#model-names
    - Цены Google: https://ai.google.dev/gemini-api/docs/pricing#gemini-2.5-pro-preview
    - Цены XAI: https://docs.x.ai/docs/models
    - Цены DeepSeek: https://api-docs.deepseek.com/quick_start/pricing
    - Цены Cerebras: https://www.cerebras.ai/pricing
    """  # noqa: E501

    def __init__(self, usd_rate: float) -> None:
        self.usd_rate = usd_rate

    @property
    @abstractmethod
    def name(self) -> str:
        """Название провайдера

        Returns:
            str: Название провайдера
        """

    @abstractmethod
    def get_models(self) -> dict[str, ModelConfig]:
        """Возвращает словарь моделей провайдера

        Returns:
            dict[str, ModelConfig]: Словарь моделей провайдера
        """

    def has_model(self, model_name: str) -> bool:
        """Проверяет, поддерживается ли модель провайдером

        Args:
            model_name (str): Название модели

        Returns:
            bool: True, если модель поддерживается, False в противном случае
        """
        return model_name in self.get_models()

    def get_model_config(self, model_name: str) -> ModelConfig:
        """Получает конфигурацию модели

        Args:
            model_name (str): Название модели

        Returns:
            ModelConfig: Конфигурация модели
        """
        models = self.get_models()
        if model_name not in models:
            raise ValueError(f'Model {model_name} not found in {self.name}')
        return models[model_name]
