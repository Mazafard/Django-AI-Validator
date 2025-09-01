# AICleanedField

`AICleanedField` is a custom model field (inheriting from `TextField`) that automatically cleans or normalizes its content using an LLM.

## Synchronous Cleaning

By default, cleaning happens during the `pre_save` signal. This blocks the save operation until the LLM responds.

```python
from django_ai_validator.fields import AICleanedField

class BlogPost(models.Model):
    content = AICleanedField(
        cleaning_prompt="Fix grammar, spelling, and improve clarity."
    )
```

## Asynchronous Cleaning

For better performance, especially with large texts or slow LLM responses, you can enable asynchronous cleaning. This requires **Celery**.

```python
class BlogPost(models.Model):
    content = AICleanedField(
        cleaning_prompt="Fix grammar, spelling, and improve clarity.",
        use_async=True
    )
```

When `use_async=True`:
1. The model is saved immediately with the original "dirty" data.
2. A Celery task is triggered.
3. The task calls the LLM and updates the field with the cleaned version.

## Configuration

- `cleaning_prompt` (required): Instructions for the LLM on how to clean the data.
- `use_async` (optional, default `False`): Whether to use a background task.
