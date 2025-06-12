import base64
from django.core.files.base import ContentFile
from .models import VideoAIContent
from core.agents.text_agent import TextAgent
from core.agents.voice_agent import VoiceAgent
import logging
logger = logging.getLogger(__name__)

def generate_text_content_util(user, video):
    # API key alma (user içinden veya settings)
    api_key = None
    if hasattr(user, 'api_keys') and getattr(user.api_keys, 'openai_api_key', None):
        api_key = user.api_keys.openai_api_key
    else:
        from django.conf import settings
        api_key = getattr(settings, 'OPENAI_API_KEY', None)

    if not api_key:
        return {'success': False, 'error': 'API key not found'}

    text_agent = TextAgent()
    response = text_agent._run(
        api_key=api_key,
        topic_title=video.title,
        prompt_context=video.description,
        duration_minutes=video.duration_minutes,
        language=video.panel.language if video.panel else 'tr'
    )

    ai_content, created = VideoAIContent.objects.update_or_create(
        video=video,
        defaults={
            'title': response.get('title', ''),
            'script': response.get('script', ''),
            'hashtags': response.get('hashtags', ''),
            'description': response.get('description', ''),
            'thumbnail_prompt': response.get('thumbnail_prompt', ''),
            'content_prompt': response.get('content_prompt', ''),
        }
    )

    video.status = 'TEXT_GENERATED'
    video.save()

    return {
        'success': True,
        'new_status': 'TEXT_GENERATED',
        'ai_content': {
            'title': response.get('title', ''),
            'description': response.get('description', ''),
            'hashtags': response.get('hashtags', []),
            'script': response.get('script', ''),
        },
        'message': 'Metin başarıyla üretildi.'
    }


def generate_voice_content_util(user, video):
    if not hasattr(video, "ai_content") or not video.ai_content.script.strip():
        return {'success': False, 'error': 'AI content script not found or empty. Please complete previous steps.'}

    api_key = None
    if hasattr(user, 'api_keys') and getattr(user.api_keys, 'tts_api_key', None):
        api_key = user.api_keys.tts_api_key

    if not api_key:
        return {'success': False, 'error': 'OpenAI API key not found for user.'}

    text = video.ai_content.script.strip()
    voice = "onyx"  # sabit erkek sesi

    agent = VoiceAgent()
    result = agent._run(api_key=api_key, text=text)
    audio_base64 = result.get("audio_base64")

    if not audio_base64:
        return {'success': False, 'error': 'No audio generated'}

    audio_bytes = base64.b64decode(audio_base64)
    audio_file = ContentFile(audio_bytes, name=f"voice_{video.id}.mp3")

    if video.voice_file:
        video.voice_file.delete(save=False)

    video.voice_file.save(audio_file.name, audio_file)
    video.save()

    return {
        'success': True,
        'voice_url': video.voice_file.url
    }

import base64
from django.core.files.base import ContentFile
from core.services.subtitle_generator import generate_subtitles_with_whisper  # core.services.subtitle_generator'dan içeri alındığını varsayıyorum
from mutagen.mp3 import MP3

def generate_subtitle_content_util(user, video):
    if not video.voice_file:
        return {'success': False, 'error': 'Voice file not found. Please complete the voice generation step first.'}

    try:
        audio_path = video.voice_file.path
        if not os.path.exists(audio_path):
            return {'success': False, 'error': 'Voice file does not exist on disk.'}
    except Exception as e:
        return {'success': False, 'error': f'Audio file error: {str(e)}'}

    try:
        # Whisper ile zaman kodlu altyazı üret
        srt_content = generate_subtitles_with_whisper(audio_path)
    except Exception as e:
        return {'success': False, 'error': f'Whisper subtitle generation failed: {str(e)}'}

    if not srt_content:
        return {'success': False, 'error': 'Subtitle generation returned empty content.'}

    # SRT dosyasını kaydet
    srt_bytes = srt_content.encode('utf-8-sig')
    srt_file = ContentFile(srt_bytes, name=f"subtitle_{video.id}.srt")

    if video.subtitle_file:
        video.subtitle_file.delete(save=False)

    video.subtitle_file.save(srt_file.name, srt_file)
    video.save()

    return {
        'success': True,
        'subtitle_file_url': video.subtitle_file.url
    }

from mutagen.mp3 import MP3
from django.core.files.base import ContentFile
from core.agents.image_content_agent import ImageContentAgent  # Agent import
from videos.models import VideoImage  # VideoImage modeli
import base64
import uuid
import math

def generate_image_content_util(user, video):
    if not hasattr(video, "ai_content") or not video.ai_content.description.strip():
        return {'success': False, 'error': 'AI description not found. Please complete text generation first.'}

    if not video.voice_file:
        return {'success': False, 'error': 'Voice file not found. Please complete voice generation first.'}

    try:
        audio = MP3(video.voice_file.path)
        duration = audio.info.length  # saniye cinsinden float
        image_count = math.floor(duration / 10)

        # Küsuratlı hesaplama: örneğin 3.7 → 4, 3.3 → 3
        fractional = (duration / 10) - image_count
        if fractional > 0.7:
            image_count += 1

    except Exception as e:
        return {'success': False, 'error': f'Failed to calculate audio duration: {str(e)}'}

    if image_count < 1:
        return {'success': False, 'error': 'Audio too short for image generation.'}

    api_key = getattr(user.api_keys, 'openai_api_key', None)
    if not api_key:
        return {'success': False, 'error': 'OpenAI API key not found for user.'}

    prompt = video.ai_content.content_prompt
    agent = ImageContentAgent()

    image_urls = []

    for i in range(image_count):
        try:
            logger.info(f"[{user}] Generating image {i+1}/{image_count} for video {video.id}")
            result = agent._run(api_key=api_key, prompt=prompt, size="1024x1024")
            image_base64 = result.get("image_base64")

            if not image_base64:
                continue

            image_data = base64.b64decode(image_base64)
            image_name = f"image_{video.id}_{uuid.uuid4().hex[:8]}.png"
            image_file = ContentFile(image_data, name=image_name)

            # Yeni image kaydı oluştur
            video_image = VideoImage.objects.create(video=video, image=image_file)
            image_urls.append(video_image.image.url)

        except Exception as e:
            logger.error(f"[{user}] Image {i+1} failed: {str(e)}")
            continue  # Her hata, sadece o resmin atlanmasına neden olur

    if not image_urls:
        return {'success': False, 'error': 'Image generation failed.'}

    return {
        'success': True,
        'images': image_urls
    }

from core.agents.image_thumbnail_agent import ImageThumbnailAgent
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import base64
import io
import uuid
import os

def generate_thumbnail_image_util(user, video):
    if not hasattr(video, "ai_content") or not video.ai_content.title.strip():
        return {'success': False, 'error': 'Title not found in AI content.'}

    api_key = getattr(user.api_keys, 'openai_api_key', None)
    if not api_key:
        return {'success': False, 'error': 'OpenAI API key not found.'}

    prompt = video.ai_content.thumbnail_prompt or "video thumbnail with abstract vibrant background"
    agent = ImageThumbnailAgent()

    try:
        # 1. OpenAI'den büyük boyutlu yatay görsel al (en yakın çözünürlük)
        result = agent._run(api_key=api_key, prompt=prompt, size="1792x1024")
        image_base64 = result.get("image_base64")
        image_data = base64.b64decode(image_base64)

        # 2. Pillow ile resmi aç, yeniden boyutlandır (bizim istediğimiz gibi)
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")
        target_size = (1024, 576)
        image = image.resize(target_size, Image.LANCZOS)

        # 3. Yazıyı yerleştir
        draw = ImageDraw.Draw(image)
        title = video.ai_content.title.strip()

        font_path = os.path.join("static", "Roboto_Condensed-Bold.ttf")
        font = ImageFont.truetype(font_path, size=64)
        text_color = (255, 255, 255, 255)
        shadow_color = (0, 0, 0, 180)

        w, h = image.size
        # Yazı konumu hesapla
        bbox = draw.textbbox((0, 0), title, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (w - tw) // 2
        y = h - th - 40

        # Gölge + yazı
        draw.text((x + 2, y + 2), title, font=font, fill=shadow_color)
        draw.text((x, y), title, font=font, fill=text_color)

        # 4. PNG olarak kaydet
        output = io.BytesIO()
        image.save(output, format="PNG")
        thumb_name = f"thumbnail_{video.id}_{uuid.uuid4().hex[:8]}.png"
        thumb_file = ContentFile(output.getvalue(), name=thumb_name)

        if video.thumbnail:
            video.thumbnail.delete(save=False)

        video.thumbnail.save(thumb_file.name, thumb_file)
        video.save()

        return {'success': True, 'thumbnail_url': video.thumbnail.url}

    except Exception as e:
        return {'success': False, 'error': str(e)}
    
import os
import uuid
from django.conf import settings
from django.core.files import File
from core.services.video_composer import compose_video  # compose_video burada
from django.core.files.base import File as DjangoFile

def generate_edit_video_util(user, video):
    # Gerekli bileşenlerin olup olmadığını kontrol et
    if not video.voice_file:
        return {'success': False, 'error': 'Voice file missing. Lütfen önce ses üretin.'}

    if not video.subtitle_file:
        return {'success': False, 'error': 'Subtitle file missing. Lütfen altyazıyı üretin.'}

    if not video.images.exists():
        return {'success': False, 'error': 'No images found. Lütfen içerik görsellerini üretin.'}

    try:
        # Yolları ayarla
        audio_path = video.voice_file.path
        srt_path = video.subtitle_file.path
        images = [img.image.path for img in video.images.all()]

        # Çıktı klasörü
        output_dir = os.path.join(settings.MEDIA_ROOT, 'final_videos')
        os.makedirs(output_dir, exist_ok=True)

        output_filename = f"final_{video.id}_{uuid.uuid4().hex[:8]}.mp4"
        output_path = os.path.join(output_dir, output_filename)

        # Videoyu oluştur
        result_path = compose_video(
            images=images,
            audio_path=audio_path,
            output_path=output_path,
            srt_path=srt_path,
            resolution=(video.panel.resolution_width, video.panel.resolution_height)
        )

        if not result_path or not os.path.exists(result_path):
            return {'success': False, 'error': 'Video composition failed or output missing.'}

        # Eski final video varsa sil
        if video.final_video:
            video.final_video.delete(save=False)

        # Yeni final videoyu kaydet
        with open(result_path, 'rb') as f:
            django_file = DjangoFile(f)
            video.final_video.save(output_filename, django_file, save=True)

        return {
            'success': True,
            'video_url': video.final_video.url
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}