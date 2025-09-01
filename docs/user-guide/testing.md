# Testing

Testing applications that use LLMs can be tricky and expensive if you hit the real API every time. `django-ai-validator` provides tools to make testing easier.

## Using the Mock Provider

The easiest way to test is to use the `mock` provider. This provider returns deterministic responses without making network requests.

### Configuration

In your `tests.py` or `conftest.py`, register the mock provider:

```python
from django.test import TestCase, override_settings
from django_ai_validator.llm.factory import LLMFactory
from django_ai_validator.llm.mock_factory import MockFactory

# Register the mock factory (do this once, e.g., in AppConfig.ready or setUpClass)
LLMFactory.register('mock', MockFactory)

@override_settings(AI_CLEANER_DEFAULT_PROVIDER='mock')
class MyModelTests(TestCase):
    def test_validation(self):
        # This will use the MockAdapter
        ...
```

### Mock Adapter Behavior

The default `MockAdapter`:
- **Validation**: Returns `False` if the input contains "bad", otherwise `True`.
- **Cleaning**: Replaces "dirty" with "clean".

You can customize this behavior by creating your own mock adapter and factory if needed.

## Mocking with `unittest.mock`

For more granular control, you can mock the `AICleaningFacade` or the underlying LLM client.

```python
from unittest.mock import patch
from django.test import TestCase
from .models import MyModel

class MyTests(TestCase):
    @patch('django_ai_validator.validators.AICleaningFacade.validate')
    def test_custom_validation(self, mock_validate):
        mock_validate.return_value = (True, None)
        
        # Your test code here
        ...
```

## Testing Asynchronous Tasks

If you are using `use_async=True`, you can test the task execution by using `celery.contrib.testing` or by mocking the task.

```python
from unittest.mock import patch

@patch('django_ai_validator.tasks.ai_clean_model_instance.delay')
def test_async_trigger(self, mock_delay):
    # Save model
    instance.save()
    
    # Verify task was called
    mock_delay.assert_called_once()
```
