# Asynchronous Cleaning

Asynchronous cleaning allows you to offload the time-consuming LLM API calls to a background worker. This ensures your application remains responsive.

## Prerequisites

You must have **Celery** installed and configured in your Django project.

1. Install Celery: `pip install celery`
2. Configure Celery in your project (see [Celery Django docs](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)).

## How to Use

Simply set `use_async=True` on your `AICleanedField`.

```python
content = AICleanedField(
    cleaning_prompt="...",
    use_async=True
)
```

## The `ai_clean_model_instance` Task

The library provides a shared task `django_ai_validator.tasks.ai_clean_model_instance`.

When `use_async=True`, this task is called with:
- `app_label`
- `model_name`
- `instance_id`
- `field_name`
- `prompt_template`

The task fetches the instance, calls the LLM, updates the field, and saves the instance.

## Considerations

- **Race Conditions**: Be aware that the field will contain the "dirty" value until the task completes.
- **Error Handling**: If the task fails (e.g., API error), the field will remain dirty. You should monitor your Celery worker logs.
