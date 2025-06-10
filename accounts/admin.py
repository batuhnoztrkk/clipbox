from django.contrib import admin
from .models import UserAPIKeys

@admin.register(UserAPIKeys)
class UserAPIKeysAdmin(admin.ModelAdmin):
    list_display = ['user', 'openai_api_key', 'tts_api_key', 'dalle_api_key', 'created_at']