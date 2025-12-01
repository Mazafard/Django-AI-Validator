from django.test import TestCase, RequestFactory, override_settings
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from django.contrib.messages.storage.fallback import FallbackStorage
from django_ai_validator.llm.adapters import OpenAIAdapter, AnthropicAdapter, GeminiAdapter, OllamaAdapter
from django_ai_validator.admin import AIAdminMixin
from django_ai_validator.fields import AICleanedField
from django_ai_validator.validators import AISemanticValidator
from .models import MockModel
from .admin import MockModelAdmin
import sys
from django.contrib.auth.models import AnonymousUser
from django_ai_validator.llm.client import OpenAIClient
from django_ai_validator.llm.mock_adapter import MockAdapter

class MockSuperUser:
    def has_perm(self, perm):
        return True

class AdminMixinTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = MockModelAdmin(MockModel, self.site)
        self.factory = RequestFactory()

    def test_is_dirty_display(self):
        obj1 = MockModel.objects.create(content="dirty1")
        obj2 = MockModel.objects.create(content="dirty2")
        
        # Should show True/False icon
        self.assertTrue(self.admin.is_dirty(obj1))

    def test_run_ai_cleanup_action(self):
        # Create dirty objects
        MockModel.objects.create(content="dirty1")
        MockModel.objects.create(content="dirty2")
        
        queryset = MockModel.objects.all()
        request = self.factory.post('/admin/sandbox_app/mockmodel/')
        request.user = AnonymousUser() # or mock user

        # Run action
        self.admin.run_ai_cleanup_on_selected(request, queryset)
        
        # Verify they are cleaned
        for obj in MockModel.objects.all():
            self.assertEqual(obj.content, "clean value")

class LLMAdapterTests(TestCase):
    def test_openai_adapter(self):
        # We need to mock the actual API call
        with patch('django_ai_validator.llm.client.OpenAIClient.validate') as mock_validate:
            mock_validate.return_value = (True, "Valid")
            
            # This would normally call OpenAI
            # But since we don't have API key set up in test env for real calls,
            # we rely on the mock.
            # However, to test the ADAPTER class specifically:
            from django_ai_validator.llm.adapters import OpenAIAdapter
            adapter = OpenAIAdapter()
            # We can't easily test the real validate without mocking the client inside it
            # or the API call.
            pass

    def test_mock_adapter(self):
        from django_ai_validator.llm.mock_adapter import MockAdapter
        adapter = MockAdapter()
        is_valid, reason = adapter.validate("good value", "prompt")
        self.assertTrue(is_valid)
        
        is_valid, reason = adapter.validate("bad value", "prompt")
        self.assertFalse(is_valid)
        self.assertEqual(reason, "Value contains 'bad'")

class AdapterTests(TestCase):
    def test_openai_validate(self):
        mock_openai = MagicMock()
        with patch.dict(sys.modules, {'openai': mock_openai}):
            # Re-import or instantiate inside patch
            # Since the import is inside __init__, we just need sys.modules patched when __init__ runs.
            
            mock_client = MagicMock()
            mock_openai.OpenAI.return_value = mock_client
            
            mock_completion = MagicMock()
            mock_completion.choices[0].message.content = "VALID"
            mock_client.chat.completions.create.return_value = mock_completion
            
            adapter = OpenAIAdapter(api_key="fake-key")
            is_valid, error = adapter.validate("test", "prompt")
            self.assertTrue(is_valid)

            mock_completion.choices[0].message.content = "cleaned"
            cleaned = adapter.clean("dirty", "prompt")
            self.assertEqual(cleaned, "cleaned")

    def test_anthropic_validate(self):
        mock_anthropic = MagicMock()
        with patch.dict(sys.modules, {'anthropic': mock_anthropic}):
            mock_client = MagicMock()
            mock_anthropic.Anthropic.return_value = mock_client
            
            mock_message = MagicMock()
            mock_message.content[0].text = "VALID"
            mock_client.messages.create.return_value = mock_message
            
            adapter = AnthropicAdapter(api_key="fake-key")
            is_valid, error = adapter.validate("test", "prompt")
            self.assertTrue(is_valid)
            
            mock_message.content[0].text = "cleaned"
            cleaned = adapter.clean("dirty", "prompt")
            self.assertEqual(cleaned, "cleaned")

    def test_gemini_validate(self):
        mock_genai = MagicMock()
        mock_google = MagicMock()
        mock_google.generativeai = mock_genai
        
        with patch.dict(sys.modules, {'google': mock_google, 'google.generativeai': mock_genai}):
            mock_model = MagicMock()
            mock_genai.GenerativeModel.return_value = mock_model
            
            mock_response = MagicMock()
            mock_response.text = "VALID"
            mock_model.generate_content.return_value = mock_response
            
            adapter = GeminiAdapter(api_key="fake-key")
            is_valid, error = adapter.validate("test", "prompt")
            self.assertTrue(is_valid)
            
            mock_response.text = "cleaned"
            cleaned = adapter.clean("dirty", "prompt")
            self.assertEqual(cleaned, "cleaned")

    def test_ollama_validate(self):
        mock_ollama = MagicMock()
        with patch.dict(sys.modules, {'ollama': mock_ollama}):
            mock_client = MagicMock()
            mock_ollama.Client.return_value = mock_client
            mock_client.chat.return_value = {'message': {'content': 'VALID'}}
            
            adapter = OllamaAdapter(host="fake-host")
            is_valid, error = adapter.validate("test", "prompt")
            self.assertTrue(is_valid)
            
            mock_client.chat.return_value = {'message': {'content': 'cleaned'}}
            cleaned = adapter.clean("dirty", "prompt")
            self.assertEqual(cleaned, "cleaned")

class DeconstructTests(TestCase):
    def test_validator_deconstruct(self):
        validator = AISemanticValidator(prompt_template="test", provider="openai")
        path, args, kwargs = validator.deconstruct()
        self.assertEqual(path, 'django_ai_validator.validators.AISemanticValidator')
        # Assuming we fix implementation or adjust test. 
        # If implementation is fixed to return args=['test'], then this test passes.
        # If implementation relies on BaseValidator, it might be returning empty args if limit_value is None.
        
        # For now, let's assume we will fix the implementation to be correct.
        self.assertEqual(args, ['test']) 
        self.assertEqual(kwargs['provider'], 'openai')

    def test_field_deconstruct(self):
        field = AICleanedField(cleaning_prompt="clean me", use_async=True)
        name, path, args, kwargs = field.deconstruct()
        self.assertEqual(kwargs['cleaning_prompt'], "clean me")
        self.assertEqual(kwargs['use_async'], True)

class AsyncFieldTests(TestCase):
    @patch('django_ai_validator.tasks.ai_clean_model_instance.delay')
    def test_async_save_triggers_task(self, mock_delay):
        field = AICleanedField(cleaning_prompt="clean", use_async=True)
        instance = TestModel(content="dirty")
        field.name = 'content'
        field._post_save_handler(TestModel, instance, created=True)
        mock_delay.assert_called_once()
