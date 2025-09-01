# Django AI Validator

**Django AI Validator** is a powerful library that leverages Large Language Models (LLMs) to validate and clean data in your Django applications. It provides seamless integration with Django models, forms, and the admin interface.

## Features

- **Semantic Validation**: Validate data based on meaning and context using LLMs (e.g., "Is this a valid professional bio?").
- **Automated Cleaning**: Automatically normalize and clean data (e.g., removing PII, fixing grammar).
- **Admin Integration**: Visual indicators for "dirty" data and bulk cleaning actions in Django Admin.
- **Asynchronous Processing**: Offload heavy LLM tasks to background workers using Celery.
- **Flexible Providers**: Support for OpenAI, Anthropic, and custom LLM providers.
- **Caching**: Built-in caching to reduce API costs and latency.

## Installation

Install the package via pip:

```bash
pip install django-ai-validator
```

Add it to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'django_ai_validator',
]
```

## Quick Start

### 1. Configure API Keys

Set your API keys in your environment variables:

```bash
export OPENAI_API_KEY="your-api-key"
```

### 2. Add a Validator

```python
from django.db import models
from django_ai_validator.validators import AISemanticValidator

class UserProfile(models.Model):
    bio = models.TextField(
        validators=[
            AISemanticValidator(
                prompt_template="Ensure this bio is professional and written in third person."
            )
        ]
    )
```

### 3. Add a Cleaned Field

```python
from django_ai_validator.fields import AICleanedField

class Comment(models.Model):
    content = AICleanedField(
        cleaning_prompt="Remove any profanity and fix spelling errors."
    )
```
