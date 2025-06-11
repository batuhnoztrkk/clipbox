from django.db import models
from panels.models import Panel

class VideoTypeChoices(models.TextChoices):
    SHORT = 'SHORT', 'Short'
    LONG = 'LONG', 'Long'

class VideoStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Bekliyor'
    GENERATING = 'GENERATING', 'Üretimde'
    ERROR = 'ERROR', 'Hata'
    COMPLETED = 'COMPLETED', 'Tamamlandı'

class Video(models.Model):
    panel = models.ForeignKey(Panel, on_delete=models.CASCADE, related_name='videos')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    video_type = models.CharField(max_length=10, choices=VideoTypeChoices.choices, default=VideoTypeChoices.SHORT)
    duration_minutes = models.PositiveIntegerField(default=1)

    # Üretim durumu
    status = models.CharField(max_length=20, choices=VideoStatusChoices.choices, default=VideoStatusChoices.PENDING)
    error_message = models.TextField(blank=True, null=True)

    # İçerikler
    voice_file = models.FileField(upload_to='voices/', blank=True, null=True)
    background_music = models.FileField(upload_to='music/', blank=True, null=True)
    final_video = models.FileField(upload_to='final_videos/', blank=True, null=True)

    # Zaman bilgisi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.panel.name} - {self.title}"

    class Meta:
        ordering = ['-created_at']

class VideoAIContent(models.Model):
    video = models.OneToOneField(Video, on_delete=models.CASCADE, related_name='ai_content')

    title = models.CharField(max_length=500)
    script = models.TextField()
    hashtags = models.JSONField()  # liste olarak JSON saklayacağız
    description = models.CharField(max_length=500)
    thumbnail_prompt = models.TextField()
    content_prompt = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class VideoImage(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='video_images/')

    def __str__(self):
        return f"Image for {self.video.title}"