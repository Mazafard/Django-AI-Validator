from django.test import TestCase
from django.core.exceptions import ValidationError
from django_ai_validator.validators import AISemanticValidator
from django.test.utils import override_settings
from .models import MockModel

@override_settings(AI_CLEANER_DEFAULT_PROVIDER='mock')
class AIValidatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from django_ai_validator.llm.factory import LLMFactory
        from django_ai_validator.llm.mock_factory import MockFactory
        LLMFactory.register('mock', MockFactory)

    def test_validator_valid(self):
        validator = AISemanticValidator(prompt_template="Check this")
        # "good" should be valid per MockLLMClient
        validator("good value")

    def test_validator_invalid(self):
        validator = AISemanticValidator(prompt_template="Check this")
        # "bad" should be invalid per MockLLMClient
        with self.assertRaises(ValidationError) as cm:
            validator("bad value")
        self.assertIn("Value contains 'bad'", str(cm.exception))

    def test_field_cleaning(self):
        obj = MockModel(content="dirty value")
        obj.save()
        self.assertEqual(obj.content, "clean value")

    def test_field_validation_on_save(self):
        # Note: Django model validation (validators) is usually run via full_clean(), not save()
        # But let's check if we can trigger it manually or if we want to enforce it in pre_save?
        # The prompt asked for "Validator Base Class", which implies standard Django validators.
        # Standard validators run during full_clean().
        
        obj = MockModel(validated_content="bad value")
        with self.assertRaises(ValidationError):
            obj.full_clean()
