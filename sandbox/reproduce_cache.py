from django_ai_validator.facade import AICleaningFacade
from django_ai_validator.cache import LLMCacheManager
from django.core.cache import cache
import time

print("--- START DEBUG ---")

# 1. Clear cache
cache.clear()
print("Cache cleared.")

facade = AICleaningFacade(provider='mock')
print(f"Provider: {facade.provider}")

# 2. First Call (Miss)
print("Call 1 (Expect 'clean data'):")
res1 = facade.clean("dirty data", "Clean this")
print(f"Result 1: {repr(res1)}")

# 3. Check Cache directly
manager = LLMCacheManager()
# Reconstruct key logic from Proxy
prompt_template = "Clean this"
value = "dirty data"
cache_key_content = f"CLEAN:{prompt_template}:{value}"
# Mock adapter model is 'mock-model'
model = "mock-model"
cached_val = manager.get(cache_key_content, model)
print(f"Direct Cache Check: {repr(cached_val)}")

# 4. Second Call (Hit)
print("Call 2 (Expect 'clean data'):")
res2 = facade.clean("dirty data", "Clean this")
print(f"Result 2: {repr(res2)}")

if res1 == res2 and res1 is not None:
    print("SUCCESS: Results match.")
else:
    print("FAILURE: Results do not match or are None.")

print("--- END DEBUG ---")
