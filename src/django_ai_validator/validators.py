from django.core.validators import BaseValidator
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from .facade import AICleaningFacade

class BaseAIValidator(BaseValidator):
    """
    Template Method Pattern: Defines the skeleton of the validation algorithm.
    """
    message = None  # Override BaseValidator's message to avoid limit_value dependency

    def __init__(self, prompt_template, provider=None, message=None, code=None):
        self.prompt_template = prompt_template
        self.provider = provider
        if code:
            self.code = code
        # BaseValidator expects a limit_value. We pass None, but then we must ensure
        # the message doesn't try to use it.
        super().__init__(limit_value=None, message=message)

    def __call__(self, value):
        # Template Method
        if self.should_skip(value):
            return

        prepared_value = self.prepare_data(value)
        is_valid, error_reason = self.execute_llm_validation(prepared_value)
        
        if not is_valid:
            self.handle_error(value, error_reason)

    def should_skip(self, value):
        return value in (None, '')

    def prepare_data(self, value):
        return str(value)

    def execute_llm_validation(self, value):
        facade = AICleaningFacade(provider=self.provider)
        return facade.validate(value, self.prompt_template)

    def handle_error(self, value, error_reason):
        raise ValidationError(
            self.message or error_reason,
            code=self.code,
            params={'value': value},
        )

    def __eq__(self, other):
        return (
            isinstance(other, BaseAIValidator) and
            self.prompt_template == other.prompt_template and
            self.message == other.message and
            self.code == other.code and
            self.provider == other.provider
        )

    def deconstruct(self):
        path = f"{self.__module__}.{self.__class__.__name__}"
        args = [self.prompt_template]
        kwargs = {}
        if self.provider:
            kwargs['provider'] = self.provider
        if self.message:
            kwargs['message'] = self.message
        if self.code:
            kwargs['code'] = self.code
        return path, args, kwargs

class AISemanticValidator(BaseAIValidator):
    """
    Concrete implementation of the validator.
    """
    pass
