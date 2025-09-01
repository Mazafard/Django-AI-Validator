import abc
import os
from typing import Tuple, Optional
from django.conf import settings
from django.utils.module_loading import import_string

class LLMClient(abc.ABC):
    """Abstract base class for LLM providers."""

    @abc.abstractmethod
    def validate(self, value: str, prompt_template: str) -> Tuple[bool, Optional[str]]:
        pass

    @abc.abstractmethod
    def clean(self, value: str, prompt_template: str) -> str:
        pass

class OpenAIClient(LLMClient):
    """Concrete implementation for OpenAI."""
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo", **kwargs):
        self.api_key = api_key or getattr(settings, 'OPENAI_API_KEY', os.environ.get("OPENAI_API_KEY"))
        self.model = model
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package is not installed. Please install 'openai'.")

    def validate(self, value: str, prompt_template: str) -> Tuple[bool, Optional[str]]:
        prompt = f"{prompt_template}\n\nInput: {value}\n\nRespond with 'VALID' if it meets the criteria. Otherwise, explain why it is invalid."
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful data validation assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )
        content = response.choices[0].message.content.strip()
        if content.upper().startswith("VALID"):
            return True, None
        else:
            return False, content

    def clean(self, value: str, prompt_template: str) -> str:
        prompt = f"{prompt_template}\n\nInput: {value}\n\nReturn ONLY the cleaned/normalized value."
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful data cleaning assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()

class AnthropicClient(LLMClient):
    """Concrete implementation for Anthropic."""
    def __init__(self, api_key: str = None, model: str = "claude-3-opus-20240229", **kwargs):
        self.api_key = api_key or getattr(settings, 'ANTHROPIC_API_KEY', os.environ.get("ANTHROPIC_API_KEY"))
        self.model = model
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic package is not installed. Please install 'anthropic'.")

    def validate(self, value: str, prompt_template: str) -> Tuple[bool, Optional[str]]:
        prompt = f"{prompt_template}\n\nInput: {value}\n\nRespond with 'VALID' if it meets the criteria. Otherwise, explain why it is invalid."
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        content = message.content[0].text.strip()
        if content.upper().startswith("VALID"):
            return True, None
        else:
            return False, content

    def clean(self, value: str, prompt_template: str) -> str:
        prompt = f"{prompt_template}\n\nInput: {value}\n\nReturn ONLY the cleaned/normalized value."
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()

class LLMClientFactory:
    """Factory to create LLM clients based on configuration."""
    
    _registry = {
        'openai': OpenAIClient,
        'anthropic': AnthropicClient,
    }

    @classmethod
    def register(cls, name: str, client_class):
        cls._registry[name] = client_class

    @classmethod
    def create(cls, provider: str = None, **kwargs) -> LLMClient:
        if not provider:
            provider = getattr(settings, 'AI_CLEANER_DEFAULT_PROVIDER', 'openai')
        
        # Check registry first
        if provider in cls._registry:
            return cls._registry[provider](**kwargs)
        
        # Try to import as dotted path
        try:
            client_class = import_string(provider)
            return client_class(**kwargs)
        except ImportError:
            raise ValueError(f"Could not resolve LLM provider: {provider}")
