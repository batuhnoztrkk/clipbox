import os
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Video
from core.services.text_generation import generate_video_script
from core.services.voice_generation import generate_voice
from core.services.image_generation import generate_image
from core.services.subtitle_generator import generate_subtitles_simple
from core.services.video_composer import compose_video
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def generate_video(request, video_id):
    video = get_object_or_404(Video, id=video_id)
    panel = video.panel
    user = panel.user

    video.status = 'GENERATING'
    video.save()

    try:
        # 1. Metin Üret
        if not video.generated_text:
            logger.info(f"Generating script for video {video.id}")
            script = generate_video_script(user, video.description, video.duration_minutes)
            video.generated_text = script
            video.save()
        else:
            logger.info(f"Using existing script for video {video.id}")
            script = video.generated_text

        # 2. Ses Üret
        voice_path = f"media/voices/voice_{video.id}.mp3"
        if not os.path.exists(voice_path):
            logger.info(f"Generating voice for video {video.id}")
            voice_binary = generate_voice(user, script)
            with open(voice_path, "wb") as f:
                f.write(voice_binary)
            video.voice_file.name = voice_path.replace("media/", "")
            video.save()
        else:
            logger.info(f"Using existing voice file for video {video.id}")

        # 3. Görsel Üret
        images = []
        images_exist = True
        for i in range(3):
            img_path = f"media/video_images/image_{video.id}_{i}.png"
            if not os.path.exists(img_path):
                images_exist = False
                break

        if images_exist:
            logger.info(f"Using existing images for video {video.id}")
            images = [f"media/video_images/image_{video.id}_{i}.png" for i in range(3)]
        else:
            logger.info(f"Generating images for video {video.id}")
            images = []
            for i in range(3):
                img_data = generate_image(user, video.title)
                img_path = f"media/video_images/image_{video.id}_{i}.png"
                with open(img_path, "wb") as f:
                    f.write(img_data)
                images.append(img_path)

        # 4. Müzik (skip for now)
        music_path = None

        # 5. Altyazı
        srt_path = f"media/subtitles/video_{video.id}.srt"
        if not os.path.exists(srt_path):
            logger.info(f"Generating subtitles for video {video.id}")
            srt_text = generate_subtitles_simple(script, duration_seconds=video.duration_minutes * 60)
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_text)
        else:
            logger.info(f"Using existing subtitles for video {video.id}")
            
        resolution = (panel.resolution_width, panel.resolution_height)
        # 6. Montaj
        output_path = f"media/final_videos/final_{video.id}.mp4"
        if not os.path.exists(output_path):
            logger.info(f"Composing final video for video {video.id}")
            compose_video(
                images=images,
                audio_path=voice_path,
                music_path=music_path,
                output_path=output_path,
                resolution=resolution,
                srt_path=srt_path,
            )
        else:
            logger.info(f"Using existing final video for video {video.id}")

        video.final_video.name = output_path.replace("media/", "")
        video.status = 'COMPLETED'
        video.save()

        return JsonResponse({'success': True, 'video': video.final_video.url})

    except Exception as e:
        logger.error(f"Error generating video {video.id}: {e}", exc_info=True)
        video.status = 'ERROR'
        video.error_message = str(e)
        video.save()
        return JsonResponse({'success': False, 'error': str(e)})
    
from django.shortcuts import render, redirect, get_object_or_404
from .models import Video
from panels.models import Panel

def video_list(request):
    videos = Video.objects.select_related('panel').all().order_by('-created_at')
    return render(request, 'videos/list.html', {'videos': videos})

def video_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST.get('description', '')
        
        duration_minutes = int(request.POST.get('duration_minutes', 1))  # duration_minutes formda gönderilmeli
        
        panel_id = int(request.POST['panel'])
        panel = get_object_or_404(Panel, id=panel_id)

        video = Video.objects.create(
            title=title,
            description=description,
            duration_minutes=duration_minutes,
            panel=panel,
            status='PENDING'
        )
        return redirect('videos:list')

    panels = Panel.objects.all()
    return render(request, 'videos/create.html', {'panels': panels})

def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    return render(request, 'videos/detail.html', {'video': video})


def video_edit(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.method == 'POST':
        video.title = request.POST.get('title', video.title)
        video.description = request.POST.get('description', video.description)
        video.length_seconds = int(request.POST.get('length_seconds', video.length_seconds))
        video.voice_type = request.POST.get('voice_type', video.voice_type)
        video.subtitle = 'subtitle' in request.POST
        panel_id = int(request.POST.get('panel', video.panel.id))
        video.panel = get_object_or_404(Panel, id=panel_id)
        video.save()
        return redirect('videos:detail', pk=video.pk)

    panels = Panel.objects.all()
    return render(request, 'videos/edit.html', {'video': video, 'panels': panels})