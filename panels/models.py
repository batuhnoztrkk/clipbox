from django.db import models
from django.contrib.auth.models import User

class PlatformChoices(models.TextChoices):
    YOUTUBE_SHORTS = 'YOUTUBE_SHORTS', 'YouTube Shorts'
    YOUTUBE_LONG = 'YOUTUBE_LONG', 'YouTube Long'
    INSTAGRAM_REELS = 'INSTAGRAM_REELS', 'Instagram Reels'
    TIKTOK = 'TIKTOK', 'TikTok'

class AdPositionChoices(models.TextChoices):
    TOP_LEFT = 'TOP_LEFT', 'Top Left'
    TOP_RIGHT = 'TOP_RIGHT', 'Top Right'
    BOTTOM_LEFT = 'BOTTOM_LEFT', 'Bottom Left'
    BOTTOM_RIGHT = 'BOTTOM_RIGHT', 'Bottom Right'
    CENTER = 'CENTER', 'Center'

class Panel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="panels")

    name = models.CharField(max_length=100)  # örn: "İlginç Bilgiler Türkçe"
    platform = models.CharField(max_length=20, choices=PlatformChoices.choices)
    language = models.CharField(max_length=10, default='tr')  # örn: 'tr', 'en'

    # Reklam ayarları
    ad_image = models.ImageField(upload_to='ads/', blank=True, null=True)
    ad_opacity = models.FloatField(default=1.0)
    ad_position = models.CharField(max_length=20, choices=AdPositionChoices.choices, default=AdPositionChoices.BOTTOM_RIGHT)

    # Bitiş ayarları
    outro_text = models.CharField(max_length=255, blank=True, null=True)
    outro_video = models.FileField(upload_to='outros/', blank=True, null=True)

    # Varsayılan içerik üretim ayarları
    default_tts_voice = models.CharField(max_length=100, blank=True, null=True)
    add_subtitles = models.BooleanField(default=True)

    # Çözünürlük
    resolution_width = models.IntegerField(default=1080)
    resolution_height = models.IntegerField(default=1920)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    class Meta:
        ordering = ['-created_at']