# Architecture

`django-ai-validator` is designed with modularity and extensibility in mind. It uses several design patterns to ensure flexibility and testability.

## Core Components

### 1. Validators (`validators.py`)
- **Pattern**: Template Method
- **Role**: `BaseAIValidator` defines the validation workflow (prepare -> validate -> handle error). Subclasses like `AISemanticValidator` implement specific logic.

### 2. Fields (`fields.py`)
- **Role**: `AICleanedField` is a custom model field that intercepts `pre_save` signals to clean data. It supports both synchronous and asynchronous modes.

### 3. Facade (`facade.py`)
- **Pattern**: Facade
- **Role**: `AICleaningFacade` provides a simplified interface for the rest of the system to interact with LLMs. It handles provider selection, caching, and error handling.

### 4. LLM Adapters (`llm/adapters.py`)
- **Pattern**: Adapter
- **Role**: Standardizes the interface for different LLM providers (OpenAI, Anthropic, etc.). Each adapter implements `validate` and `clean` methods.

### 5. Factory (`llm/factory.py`)
- **Pattern**: Abstract Factory / Registry
- **Role**: `LLMFactory` creates instances of adapters based on configuration. It allows registration of custom providers.

### 6. Proxy (`llm/proxy.py`)
- **Pattern**: Proxy
- **Role**: `CachingLLMProxy` wraps adapters to add caching behavior without modifying the adapter code.

### 7. Cache Manager (`cache.py`)
- **Pattern**: Singleton
- **Role**: `LLMCacheManager` handles generating cache keys and interacting with Django's cache framework.

## Data Flow

1. **Input**: User submits data (e.g., via Form or Admin).
2. **Validator/Field**: The validator or field intercepts the data.
3. **Facade**: The request is passed to the `AICleaningFacade`.
4. **Factory**: The facade asks the factory for the configured LLM adapter.
5. **Proxy**: The factory returns a proxy (if caching is enabled) wrapping the adapter.
6. **Cache Check**: The proxy checks if the result is in the cache.
7. **LLM Call**: If not cached, the adapter calls the external LLM API.
8. **Result**: The result is returned, cached, and passed back to the validator/field.
9. **Action**: The validator raises `ValidationError` or the field updates the model instance.
