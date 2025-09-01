# Custom Providers

`django-ai-validator` supports OpenAI, Anthropic, Gemini, and Ollama out of the box. However, you can easily add support for other LLM providers (e.g., Cohere, Azure OpenAI, local models) by implementing a custom adapter.

## 1. Create an Adapter

Create a class that inherits from `django_ai_validator.llm.adapters.LLMAdapter` and implements the `validate` and `clean` methods.

```python
from typing import Tuple, Optional
from django_ai_validator.llm.adapters import LLMAdapter

class MyCustomAdapter(LLMAdapter):
    def __init__(self, api_key=None, **kwargs):
        self.api_key = api_key
        # Initialize your client here
        
    def validate(self, value: str, prompt_template: str) -> Tuple[bool, Optional[str]]:
        # Call your LLM API
        # Return (True, None) if valid
        # Return (False, "Reason") if invalid
        pass

    def clean(self, value: str, prompt_template: str) -> str:
        # Call your LLM API
        # Return the cleaned string
        pass
```

## 2. Create a Factory

Create a factory class that returns an instance of your adapter.

```python
class MyCustomFactory:
    @staticmethod
    def create_adapter(**kwargs):
        return MyCustomAdapter(**kwargs)
```

## 3. Register the Provider

Register your factory with the `LLMFactory` in your Django app's `ready` method.

```python
# apps.py
from django.apps import AppConfig
from django_ai_validator.llm.factory import LLMFactory
from .adapters import MyCustomFactory

class MyAppConfig(AppConfig):
    name = 'my_app'

    def ready(self):
        LLMFactory.register('my_provider', MyCustomFactory)
```

## 4. Use the Provider

You can now use your custom provider in validators and fields.

```python
# settings.py
AI_CLEANER_DEFAULT_PROVIDER = 'my_provider'

# OR in a validator
validator = AISemanticValidator(..., provider='my_provider')
```
