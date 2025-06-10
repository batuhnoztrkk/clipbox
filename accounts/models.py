from django.db import models
from django.contrib.auth.models import User

class UserAPIKeys(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="api_keys")
    
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    tts_api_key = models.CharField(max_length=255, blank=True, null=True)
    dalle_api_key = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s API Keys"
