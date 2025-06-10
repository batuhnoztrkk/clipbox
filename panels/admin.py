from django.contrib import admin
from .models import Panel

@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'platform', 'language', 'is_active', 'created_at']
    list_filter = ['platform', 'language', 'is_active']
