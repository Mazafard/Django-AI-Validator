from django.test import TestCase, RequestFactory, override_settings
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from unittest.mock import patch, MagicMock
from django.contrib.messages.storage.fallback import FallbackStorage
from django_ai_validator.llm.adapters import OpenAIAdapter, AnthropicAdapter, GeminiAdapter, OllamaAdapter
from django_ai_validator.admin import AIAdminMixin
from django_ai_validator.fields import AICleanedField
from django_ai_validator.validators import AISemanticValidator
from .models import TestModel
from .admin import TestModelAdmin
import sys

class MockSuperUser:
    def has_perm(self, perm):
        return True

class AdminMixinTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = TestModelAdmin(TestModel, self.site)
        self.factory = RequestFactory()

    @override_settings(AI_CLEANER_DEFAULT_PROVIDER='mock')
    def test_run_ai_cleanup_action(self):
        obj1 = TestModel.objects.create(content="dirty1")
        obj2 = TestModel.objects.create(content="dirty2")
        
        request = self.factory.post('/admin/sandbox_app/testmodel/')
        request.user = MockSuperUser()
        
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        
        queryset = TestModel.objects.all()
        self.admin.run_ai_cleanup_on_selected(request, queryset)
        
        obj1.refresh_from_db()
        obj2.refresh_from_db()
        
        # MockAdapter replaces "dirty" with "clean"
        self.assertEqual(obj1.content, "clean1") 
        self.assertEqual(obj2.content, "clean2")

    def test_list_display_includes_is_dirty(self):
        request = self.factory.get('/admin/')
        list_display = self.admin.get_list_display(request)
        self.assertIn('is_dirty', list_display)

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
