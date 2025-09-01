from celery import shared_task
from django.apps import apps
from django.conf import settings
from django.utils.module_loading import import_string

@shared_task
def ai_clean_model_instance(app_label, model_name, instance_id, field_name, prompt_template):
    Model = apps.get_model(app_label, model_name)
    try:
        instance = Model.objects.get(pk=instance_id)
    except Model.DoesNotExist:
        return f"Instance {instance_id} not found."

    # Get LLM Client
    from .llm.client import LLMClientFactory
    client = LLMClientFactory.create()

    current_value = getattr(instance, field_name)
    if current_value:
        cleaned_value = client.clean(current_value, prompt_template)
        setattr(instance, field_name, cleaned_value)
        
        # If using AIDirtyMixin, we might want to clear the dirty flag
        if hasattr(instance, 'is_dirty'):
            instance.is_dirty = False
            
        instance.save()
        return f"Cleaned {field_name} for instance {instance_id}"
    return "No value to clean."
