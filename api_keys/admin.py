from django.contrib import admin
from .models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'key_preview', 'is_active', 'created_at', 'last_used']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'user__username', 'key']
    readonly_fields = ['key', 'created_at', 'last_used']

    def key_preview(self, obj):
        return f"{obj.key[:20]}..."

    key_preview.short_description = 'API Key'