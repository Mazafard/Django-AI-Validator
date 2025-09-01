from typing import Tuple, Optional
from .llm.factory import LLMFactory
from .llm.proxy import CachingLLMProxy

class AICleaningFacade:
    """
    Facade Pattern: Provides a simplified interface to the complex subsystem 
    (Factory, Adapter, Proxy, Cache).
    """
    def __init__(self, provider: str = None):
        self.provider = provider

    def _get_client(self):
        # 1. Get Factory
        factory = LLMFactory.get_factory(self.provider)
        # 2. Create Adapter
        adapter = factory.create_adapter()
        # 3. Wrap in Proxy for Caching
        return CachingLLMProxy(adapter)

    def validate(self, value: str, prompt_template: str) -> Tuple[bool, Optional[str]]:
        client = self._get_client()
        return client.validate(value, prompt_template)

    def clean(self, value: str, prompt_template: str) -> str:
        client = self._get_client()
        return client.clean(value, prompt_template)
