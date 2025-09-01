import hashlib
from django.core.cache import cache

class LLMCacheManager:
    """
    Singleton class to manage caching of LLM responses.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMCacheManager, cls).__new__(cls)
        return cls._instance

    def _generate_key(self, prompt: str, model: str) -> str:
        # Create a unique hash for the prompt and model
        raw_key = f"{model}:{prompt}"
        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    def get(self, prompt: str, model: str):
        key = self._generate_key(prompt, model)
        return cache.get(key)

    def set(self, prompt: str, model: str, value: str, timeout: int = 3600):
        key = self._generate_key(prompt, model)
        cache.set(key, value, timeout)
