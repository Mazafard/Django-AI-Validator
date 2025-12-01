from django.contrib import admin
from django_ai_validator.admin import AIAdminMixin
from .models import MockModel

@admin.register(MockModel)
class MockModelAdmin(AIAdminMixin, admin.ModelAdmin):
    list_display = ['id', 'content', 'validated_content', 'is_dirty']
    
    # Add is_dirty property to model for display if it doesn't exist
    def is_dirty(self, obj):
        return getattr(obj, 'is_dirty', False)
    is_dirty.boolean = True
