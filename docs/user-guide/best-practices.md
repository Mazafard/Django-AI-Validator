# Best Practices

## Prompt Engineering

The quality of validation and cleaning depends heavily on your prompts.

- **Be Specific**: Clearly state what is allowed and what is not.
- **Provide Examples**: Few-shot prompting (giving examples in the prompt) can significantly improve accuracy.
- **Use Delimiters**: Use quotes or other delimiters to separate the input value from the instructions.

**Example:**
> "Check if the following text is a valid address. Return VALID if yes. Text: '{value}'"

## Cost Management

LLM APIs can be expensive.

- **Use Caching**: Enable caching (enabled by default) to avoid paying for the same validation twice.
- **Use Cheaper Models**: For simple tasks, use cheaper models like `gpt-3.5-turbo` or `gemini-pro` instead of `gpt-4`.
- **Validate Locally First**: Use standard Django validators (e.g., `MaxLengthValidator`, `EmailValidator`) to catch obvious errors *before* calling the LLM.

```python
validators=[
    MaxLengthValidator(500),  # Cheap check first
    AISemanticValidator(...)  # Expensive check second
]
```

## Error Handling

LLM APIs can fail (timeouts, rate limits).

- **Synchronous**: If the API fails during a synchronous save, a `ValidationError` or `ImportError` (if missing deps) might be raised. Ensure your UI handles these gracefully.
- **Asynchronous**: If using `AICleanedField(use_async=True)`, failures happen in the background. Monitor your Celery logs. The field will remain "dirty" if the task fails.

## Security

- **Prompt Injection**: Be aware that malicious users might try to inject instructions into the input to manipulate the LLM.
- **Sanitization**: Always sanitize the output of the LLM if you plan to render it as HTML (though `AICleanedField` returns text, be careful how you use it).
