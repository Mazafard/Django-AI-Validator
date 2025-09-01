import abc
import os
from typing import Tuple, Optional
from django.conf import settings

class LLMAdapter(abc.ABC):
    """
    Target interface for the Adapter Pattern.
    Standardizes interaction with different LLM providers.
    """
    @abc.abstractmethod
    def validate(self, value: str, prompt_template: str) -> Tuple[bool, Optional[str]]:
        pass

    @abc.abstractmethod
    def clean(self, value: str, prompt_template: str) -> str:
        pass

class OpenAIAdapter(LLMAdapter):
    """Adapter for OpenAI API."""
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

class AnthropicAdapter(LLMAdapter):
    """Adapter for Anthropic API."""
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

class GeminiAdapter(LLMAdapter):
    """Adapter for Google Gemini API."""
    def __init__(self, api_key: str = None, model: str = "gemini-pro", **kwargs):
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', os.environ.get("GEMINI_API_KEY"))
        self.model = model
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        except ImportError:
            raise ImportError("Google Generative AI package is not installed. Please install 'google-generativeai'.")

    def validate(self, value: str, prompt_template: str) -> Tuple[bool, Optional[str]]:
        prompt = f"{prompt_template}\n\nInput: {value}\n\nRespond with 'VALID' if it meets the criteria. Otherwise, explain why it is invalid."
        response = self.client.generate_content(prompt)
        content = response.text.strip()
        if content.upper().startswith("VALID"):
            return True, None
        else:
            return False, content

    def clean(self, value: str, prompt_template: str) -> str:
        prompt = f"{prompt_template}\n\nInput: {value}\n\nReturn ONLY the cleaned/normalized value."
        response = self.client.generate_content(prompt)
        return response.text.strip()

class OllamaAdapter(LLMAdapter):
    """Adapter for Ollama (Llama) API."""
    def __init__(self, host: str = None, model: str = "llama3", **kwargs):
        self.host = host or getattr(settings, 'OLLAMA_HOST', os.environ.get("OLLAMA_HOST"))
        self.model = model
        try:
            import ollama
            self.client = ollama.Client(host=self.host)
        except ImportError:
            raise ImportError("Ollama package is not installed. Please install 'ollama'.")

    def validate(self, value: str, prompt_template: str) -> Tuple[bool, Optional[str]]:
        prompt = f"{prompt_template}\n\nInput: {value}\n\nRespond with 'VALID' if it meets the criteria. Otherwise, explain why it is invalid."
        response = self.client.chat(model=self.model, messages=[
            {'role': 'user', 'content': prompt},
        ])
        content = response['message']['content'].strip()
        if content.upper().startswith("VALID"):
            return True, None
        else:
            return False, content

    def clean(self, value: str, prompt_template: str) -> str:
        prompt = f"{prompt_template}\n\nInput: {value}\n\nReturn ONLY the cleaned/normalized value."
        response = self.client.chat(model=self.model, messages=[
            {'role': 'user', 'content': prompt},
        ])
        return response['message']['content'].strip()
