from django.contrib import admin
from .models import Video, VideoImage, VideoAIContent

class VideoImageInline(admin.TabularInline):
    model = VideoImage
    extra = 0

class VideoAIContentInline(admin.TabularInline):
    model = VideoAIContent
    extra = 0

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'panel', 'video_type', 'status', 'created_at']
    list_filter = ['video_type', 'status']
    inlines = [VideoImageInline, VideoAIContentInline]
