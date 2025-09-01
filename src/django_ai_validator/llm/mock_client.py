from django_ai_validator.llm.client import LLMClient
from typing import Tuple, Optional

class MockLLMClient(LLMClient):
    def validate(self, value: str, prompt_template: str) -> Tuple[bool, Optional[str]]:
        if "bad" in value:
            return False, "Value contains 'bad'"
        return True, None

    def clean(self, value: str, prompt_template: str) -> str:
        return value.replace("dirty", "clean")
