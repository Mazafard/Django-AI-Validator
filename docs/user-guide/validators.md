# Validators

The `AISemanticValidator` allows you to perform complex semantic validation that traditional regex or logic-based validators cannot handle.

## Usage

Import the validator and add it to your model or form field's `validators` list.

```python
from django_ai_validator.validators import AISemanticValidator

name = models.CharField(
    max_length=100,
    validators=[
        AISemanticValidator(
            prompt_template="Check if this is a valid full name (First Last). It should not be a company name."
        )
    ]
)
```

## How it Works

The validator sends the field's value along with your `prompt_template` to the configured LLM. The LLM is instructed to determine if the value meets the criteria.

- If valid, the LLM returns "VALID".
- If invalid, the LLM returns an explanation, which is raised as a `ValidationError`.

## Customizing the Provider

You can specify a different LLM provider for a specific validator:

```python
AISemanticValidator(
    prompt_template="...",
    provider="anthropic"  # Use Anthropic instead of the default
)
```
