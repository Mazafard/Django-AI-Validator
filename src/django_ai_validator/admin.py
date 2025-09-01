from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.conf import settings
from django.utils.module_loading import import_string

class AIAdminMixin:
    actions = ['run_ai_cleanup_on_selected']

    @admin.action(description=_("Run AI Cleanup on selected items"))
    def run_ai_cleanup_on_selected(self, request, queryset):
        # This assumes the model has AICleanedFields or similar logic
        # For now, we'll iterate and call save() which triggers pre_save cleaning
        # In a real scenario, we might want to be more selective or use async tasks
        
        count = 0
        for obj in queryset:
            # We can also check for is_dirty if it exists
            obj.save()
            count += 1
        
        self.message_user(request, _(f"Successfully ran AI cleanup on {count} items."), messages.SUCCESS)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if 'is_dirty' not in list_display and hasattr(self.model, 'is_dirty'):
             return list_display + ('is_dirty',)
        return list_display
