from django.test import TestCase
from django.core.exceptions import ValidationError
from django_ai_validator.validators import AISemanticValidator
from django.test.utils import override_settings
from .models import TestModel

@override_settings(AI_CLEANER_DEFAULT_PROVIDER='mock')
class AICleanerTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from django_ai_validator.llm.factory import LLMFactory
        from django_ai_validator.llm.mock_factory import MockFactory
        LLMFactory.register('mock', MockFactory)

    def test_validator_valid(self):
        validator = AISemanticValidator(prompt_template="Check this")
        # "good" should be valid per MockAdapter
        validator("good value")

    def test_validator_invalid(self):
        validator = AISemanticValidator(prompt_template="Check this")
        # "bad" should be invalid per MockAdapter
        with self.assertRaises(ValidationError) as cm:
            validator("bad value")
        self.assertIn("Value contains 'bad'", str(cm.exception))

    def test_field_cleaning(self):
        obj = TestModel(content="dirty value")
        obj.save()
        self.assertEqual(obj.content, "clean value")

    def test_field_validation_on_save(self):
        obj = TestModel(validated_content="bad value")
        with self.assertRaises(ValidationError):
            obj.full_clean()
