from typing import Tuple, Optional
from .adapters import LLMAdapter
from ..cache import LLMCacheManager

class CachingLLMProxy(LLMAdapter):
    """
    Proxy Pattern: Wraps an LLMAdapter to add caching behavior.
    """
    def __init__(self, adapter: LLMAdapter):
        self.adapter = adapter
        self.cache_manager = LLMCacheManager()

    def validate(self, value: str, prompt_template: str) -> Tuple[bool, Optional[str]]:
        # We cache the raw validation result. 
        # Note: Complex objects like (bool, str) need serialization if using non-pickle cache,
        # but Django's default LocMemCache handles python objects.
        
        # Construct a unique key based on inputs
        cache_key_content = f"VALIDATE:{prompt_template}:{value}"
        cached_result = self.cache_manager.get(cache_key_content, self.adapter.model)
        
        if cached_result is not None:
            return cached_result

        result = self.adapter.validate(value, prompt_template)
        self.cache_manager.set(cache_key_content, self.adapter.model, result)
        return result

    def clean(self, value: str, prompt_template: str) -> str:
        cache_key_content = f"CLEAN:{prompt_template}:{value}"
        cached_result = self.cache_manager.get(cache_key_content, self.adapter.model)
        
        if cached_result is not None:
            return cached_result

        result = self.adapter.clean(value, prompt_template)
        self.cache_manager.set(cache_key_content, self.adapter.model, result)
        return result
