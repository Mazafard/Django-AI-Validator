from django.db import models

class AIDirtyMixin(models.Model):
    is_dirty = models.BooleanField(default=False, help_text="Flag indicating if the data needs AI cleaning/validation.")

    class Meta:
        abstract = True
