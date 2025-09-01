from django.apps import AppConfig

class SandboxAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sandbox_app'

    def ready(self):
        # Register the mock provider so it's available in shell and tests
        from django_ai_validator.llm.factory import LLMFactory
        from django_ai_validator.llm.mock_factory import MockFactory
        LLMFactory.register('mock', MockFactory)
