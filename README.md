# Django AI Validator

[![PyPI version](https://badge.fury.io/py/django-ai-validator.svg)](https://badge.fury.io/py/django-ai-validator)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/Mazafard/Django-AI-Validator/graph/badge.svg?token=SOQZ6ZCHZD)](https://codecov.io/gh/Mazafard/Django-AI-Validator)
[![Documentation](https://img.shields.io/badge/docs-latest-blue)](https://mazafard.github.io/django-ai-validator/)

**Documentation**: [https://mazafard.github.io/django-ai-validator/](https://mazafard.github.io/django-ai-validator/)

A Django library for AI-powered data validation and cleaning.

## Features

- **Semantic Validation**: Validate data based on meaning using LLMs.
- **Automated Cleaning**: Automatically clean and normalize data.
- **Admin Integration**: Bulk actions and status indicators in Django Admin.
- **Asynchronous Support**: Offload LLM calls to Celery tasks.
- **Multiple Providers**: Support for OpenAI, Anthropic, Gemini, and Ollama.

## Installation

```bash
pip install django-ai-validator
```

## Configuration

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_ai_validator',
]
```

Set your API key:

```python
# Defaults to OpenAIClient
AI_CLEANER_LLM_CLIENT = 'django_ai_validator.llm.client.OpenAIClient'
OPENAI_API_KEY = "your-api-key"
```

## Usage

### Semantic Validation

```python
from django.db import models
from django_ai_validator.validators import AISemanticValidator

class Product(models.Model):
    description = models.TextField(
        validators=[
            AISemanticValidator(
                prompt_template="Ensure the description is marketing-friendly and contains no offensive language."
            )
        ]
    )
```

### Automatic Cleaning

```python
from django_ai_validator.fields import AICleanedField

class UserProfile(models.Model):
    bio = AICleanedField(
        cleaning_prompt="Fix grammar and remove personal contact info."
    )
```

### Admin Integration

```python
from django.contrib import admin
from django_ai_validator.admin import AIAdminMixin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(AIAdminMixin, admin.ModelAdmin):
    list_display = ['content', 'is_dirty']
    actions = ['run_ai_cleanup_on_selected']
```

### Manual Validation

To check if user input contains bad words:

```python
from django_ai_validator.validators import AISemanticValidator

class Comment(models.Model):
    text = models.TextField(
        validators=[
            AISemanticValidator(
                prompt_template="Check if this text contains bad words. Return VALID if not."
            )
        ]
    )
```

### Asynchronous Cleaning

To automatically remove personal information:

```python
from django_ai_validator.fields import AICleanedField

class Feedback(models.Model):
    message = AICleanedField(
        cleaning_prompt="Remove PII.",
    )
```


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mazafard/django-ai-validator&type=Date)](https://star-history.com/#mazafard/django-ai-validator&Date)
