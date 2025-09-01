from django.db import models
from django_ai_validator.validators import AISemanticValidator
from django_ai_validator.fields import AICleanedField

class TestModel(models.Model):
    content = AICleanedField(cleaning_prompt="Clean this", blank=True)
    validated_content = models.CharField(
        max_length=100,
        validators=[AISemanticValidator(prompt_template="Validate this")],
        blank=True
    )
