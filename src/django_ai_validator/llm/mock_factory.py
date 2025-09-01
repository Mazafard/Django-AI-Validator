from django_ai_validator.llm.factory import AIProviderFactory
from django_ai_validator.llm.adapters import LLMAdapter
from .mock_adapter import MockAdapter

class MockFactory(AIProviderFactory):
    def create_adapter(self, **kwargs) -> LLMAdapter:
        return MockAdapter(**kwargs)
