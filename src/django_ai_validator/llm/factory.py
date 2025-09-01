import abc
from django.conf import settings
from django.utils.module_loading import import_string
from .adapters import LLMAdapter, OpenAIAdapter, AnthropicAdapter

class AIProviderFactory(abc.ABC):
    """
    Abstract Factory for creating families of AI-related objects.
    """
    @abc.abstractmethod
    def create_adapter(self, **kwargs) -> LLMAdapter:
        pass

class OpenAIFactory(AIProviderFactory):
    def create_adapter(self, **kwargs) -> LLMAdapter:
        return OpenAIAdapter(**kwargs)

class AnthropicFactory(AIProviderFactory):
    def create_adapter(self, **kwargs) -> LLMAdapter:
        return AnthropicAdapter(**kwargs)

class GeminiFactory(AIProviderFactory):
    def create_adapter(self, **kwargs) -> LLMAdapter:
        from .adapters import GeminiAdapter
        return GeminiAdapter(**kwargs)

class OllamaFactory(AIProviderFactory):
    def create_adapter(self, **kwargs) -> LLMAdapter:
        from .adapters import OllamaAdapter
        return OllamaAdapter(**kwargs)

class LLMFactory:
    """
    Simple Factory / Registry to get the correct Abstract Factory.
    """
    _registry = {
        'openai': OpenAIFactory,
        'anthropic': AnthropicFactory,
        'gemini': GeminiFactory,
        'ollama': OllamaFactory,
    }

    @classmethod
    def register(cls, name: str, factory_class):
        cls._registry[name] = factory_class

    @classmethod
    def get_factory(cls, provider: str = None) -> AIProviderFactory:
        if not provider:
            provider = getattr(settings, 'AI_CLEANER_DEFAULT_PROVIDER', 'openai')
        
        factory_class = cls._registry.get(provider)
        if not factory_class:
            # Try import string
            try:
                factory_class = import_string(provider)
            except ImportError:
                raise ValueError(f"Unknown provider: {provider}")
        
        return factory_class()
