# Admin Integration

Django AI Validator provides tools to integrate AI capabilities directly into the Django Admin interface.

## AIAdminMixin

Use `AIAdminMixin` in your `ModelAdmin` to enable bulk cleaning actions.

```python
from django.contrib import admin
from django_ai_validator.admin import AIAdminMixin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(AIAdminMixin, admin.ModelAdmin):
    list_display = ['content', 'is_dirty']
    actions = ['run_ai_cleanup_on_selected']
```

### Features

- **`run_ai_cleanup_on_selected` Action**: Select multiple rows and run the AI cleaning process on them. This is useful for batch processing existing data.
- **`is_dirty` Flag**: If your model uses `AIDirtyMixin`, you can display the `is_dirty` status in the admin list view.

## AIDirtyMixin

Add `AIDirtyMixin` to your models to track whether they need cleaning.

```python
from django_ai_validator.models import AIDirtyMixin

class MyModel(AIDirtyMixin, models.Model):
    ...
```

This adds an `is_dirty` boolean field (default `True`). You can use this in your application logic to determine which records need processing.
