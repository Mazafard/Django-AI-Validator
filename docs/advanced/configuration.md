# Configuration

You can configure Django AI Validator in your `settings.py`.

## Default Provider

Set the default LLM provider for the entire project:

```python
AI_CLEANER_DEFAULT_PROVIDER = 'openai'  # 'anthropic', 'gemini', or 'ollama'
```

## API Keys

Ensure your API keys are set in your environment variables:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY` (for Google Gemini)
- `OLLAMA_HOST` (optional, defaults to localhost:11434 for Ollama)

## Caching

The library uses Django's cache framework to cache LLM responses. This saves money and time for repeated identical requests.

To configure the cache timeout (in seconds):

```python
# settings.py
AI_CLEANER_CACHE_TIMEOUT = 3600  # Default is 1 hour
```

## Registering Custom Providers

You can register your own LLM providers using the `LLMFactory`.

```python
# apps.py in your app
from django.apps import AppConfig
from django_ai_validator.llm.factory import LLMFactory
from .my_custom_provider import MyCustomFactory

class MyAppConfig(AppConfig):
    def ready(self):
        LLMFactory.register('my_provider', MyCustomFactory)
```
