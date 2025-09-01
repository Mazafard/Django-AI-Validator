from django.db import models
from django.conf import settings
from django.utils.module_loading import import_string

class AICleanedField(models.TextField):
    description = "A text field that is automatically cleaned by AI before saving."

    def __init__(self, *args, cleaning_prompt=None, use_async=False, **kwargs):
        self.cleaning_prompt = cleaning_prompt
        self.use_async = use_async
        super().__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only)
        if self.use_async:
            from django.db.models.signals import post_save
            post_save.connect(self._post_save_handler, sender=cls)

    def _post_save_handler(self, sender, instance, created, **kwargs):
        # Avoid infinite recursion if the task saves the instance again
        # The task should handle this, or we check if it's already clean
        # For now, we just trigger the task
        from .tasks import ai_clean_model_instance
        # We need to pass the app label and model name
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        
        # Only trigger if the field has a value
        value = getattr(instance, self.name)
        if value:
             ai_clean_model_instance.delay(
                app_label, 
                model_name, 
                instance.pk, 
                self.name, 
                self.cleaning_prompt
            )

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        
        if self.use_async:
            # If async, we don't clean here. We wait for post_save.
            return value

        if value and self.cleaning_prompt:
            from .facade import AICleaningFacade
            # TODO: Allow configuring provider on the field
            facade = AICleaningFacade()
            cleaned_value = facade.clean(value, self.cleaning_prompt)
            setattr(model_instance, self.attname, cleaned_value)
            return cleaned_value
        return value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.cleaning_prompt:
            kwargs['cleaning_prompt'] = self.cleaning_prompt
        if self.use_async:
            kwargs['use_async'] = self.use_async
        return name, path, args, kwargs
