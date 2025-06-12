from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from .models import Video, VideoAIContent
from django.utils.decorators import method_decorator
import logging
import base64
from .utils import generate_text_content_util, generate_voice_content_util, generate_subtitle_content_util, generate_image_content_util, generate_thumbnail_image_util, generate_edit_video_util
logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def generate_content(request, video_id, step):
    if request.method != 'POST':
        logger.warning(f"[{request.user}] Invalid request method: {request.method} on step={step}")
        return JsonResponse({'success': False, 'error': 'Only POST method allowed'}, status=405)

    if step not in ['text', 'voice', 'subtitle', 'content_images', 'banner_image', 'thumbnail_image', 'edit']:
        logger.warning(f"[{request.user}] Invalid step parameter: {step}")
        return JsonResponse({'success': False, 'error': 'Invalid step parameter'}, status=400)

    video = get_object_or_404(Video, id=video_id)

    try:
        user = request.user
        logger.info(f"[{user}] Step `{step}` generation started for video {video.id} - `{video.title}`")

        if step == 'text':
            response = generate_text_content_util(user, video)
        elif step == 'voice':
            response = generate_voice_content_util(user, video)
        elif step == 'subtitle':
            response = generate_subtitle_content_util(user, video)
        elif step == 'content_images':
            response = generate_image_content_util(user, video)
        elif step == 'thumbnail_image':
            response = generate_thumbnail_image_util(user, video)
        elif step == 'edit':
            response = generate_edit_video_util(user, video)
        else:
            response = {'success': False, 'error': 'Unsupported step'}

        if response.get('success'):
            logger.info(f"[{user}] Step `{step}` generation SUCCESS for video {video.id}")
        else:
            logger.error(f"[{user}] Step `{step}` generation FAILED for video {video.id} - Reason: {response.get('error')}")

        return JsonResponse(response)

    except Exception as e:
        logger.exception(f"[{request.user}] Exception occurred in step `{step}` for video {video.id}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


from django.shortcuts import render, redirect, get_object_or_404
from .models import Video
from panels.models import Panel

def video_list(request):
    panel_id = request.GET.get("panel_id")
    videos = Video.objects.all()
    if panel_id:
        videos = videos.filter(panel_id=panel_id)
    return render(request, "videos/list.html", {"videos": videos})

def video_create(request, panel_id):
    panel = get_object_or_404(Panel, id=panel_id)

    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST.get('description', '')
        duration_seconds = int(request.POST.get('length_seconds', 60))  # saniye olarak geliyor
        voice_type = request.POST.get('voice_type', 'female')
        subtitle = bool(request.POST.get('subtitle'))

        # dakika cinsinden kaydetmek istiyorsan:
        duration_minutes = round(duration_seconds / 60, 2)

        video = Video.objects.create(
            title=title,
            description=description,
            duration_minutes=duration_minutes,
            panel=panel,
            status='PENDING',
        )
        return redirect('panels:detail', pk=panel.id)

    return render(request, 'videos/create.html', {'panel': panel})

def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    
    # İlişkili verileri sorgula ve hazırla
    try:
        ai_content = video.ai_content  # OneToOne veya ForeignKey ise
    except Video.ai_content.RelatedObjectDoesNotExist:
        ai_content = None
    
    images = video.images.all()  # related_name='images' varsayımı
    voice_file = video.voice_file if hasattr(video, 'voice_file') else None
    subtitle_file = video.subtitle_file if hasattr(video, 'subtitle_file') else None
    
    context = {
        'video': video,
        'ai_content': ai_content,
        'images': images,
        'voice_file': voice_file,
        'subtitle_file': subtitle_file,
    }
    return render(request, 'videos/detail.html', context)


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