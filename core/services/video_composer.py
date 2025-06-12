import os
import re
import logging
import uuid
from moviepy import (
    ImageClip,
    concatenate_videoclips,
    AudioFileClip,
    CompositeAudioClip,
    TextClip,
    CompositeVideoClip,
    VideoFileClip,
)
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.CrossFadeIn import CrossFadeIn
from moviepy.video.tools.subtitles import SubtitlesClip
from django.conf import settings
logger = logging.getLogger(__name__)


def parse_srt(srt_text):
    subtitles = []
    entries = re.split(r'\n\s*\n', srt_text.strip())

    for entry in entries:
        lines = entry.strip().split("\n")
        if len(lines) >= 3:
            time_line = lines[1]
            start_str, end_str = time_line.split(" --> ")

            def time_to_seconds(t):
                match = re.match(r"(\d+):(\d+):(\d+),(\d+)", t)
                if not match:
                    raise ValueError(f"Invalid time format: {t}")
                h, m, s, ms = map(int, match.groups())
                return h * 3600 + m * 60 + s + ms / 1000

            start = time_to_seconds(start_str)
            end = time_to_seconds(end_str)
            text = " ".join(lines[2:])
            subtitles.append(((start, end), text))

    return subtitles

def make_zoom_effect(image_path, duration, resolution, zoom_ratio):
    img_clip = ImageClip(image_path)
    w, h = img_clip.size

    def make_frame(t):
        zoom = 1.0 + zoom_ratio * (t / duration)
        frame = img_clip.get_frame(0)  # Görsel sabit
        resized = Resize(lambda _: zoom)(ImageClip(frame))
        return resized.resize(resolution).get_frame(0)

    return VideoClip(make_frame=make_frame, duration=duration).set_duration(duration)

def compose_video(
    images,
    audio_path,
    output_path="output.mp4",
    music_path=None,
    resolution=(1280, 720),
    srt_path=None,
):
    try:
        print("🎬 Starting video composition")

        if not images:
            logger.error("No images provided.")
            return None

        print(f"🖼️ Video resolution: {resolution}")

        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        print(f"🔊 Audio loaded. Duration: {audio_duration:.2f}s")

        # Background music
        if music_path and os.path.isfile(music_path):
            music = AudioFileClip(music_path).volumex(0.3)
            final_audio = CompositeAudioClip([audio, music.set_duration(audio.duration)])
        else:
            final_audio = audio

        clip_duration = audio_duration / len(images)

        transition_duration = 1.0  # saniye cinsinden geçiş süresi

        clips = []

        for idx, img_path in enumerate(images):
            print(f"📷 Processing image {idx + 1}/{len(images)}: {img_path}")

            try:
                zoom_ratio = 0.2
                # Görseli süreyle birlikte klip haline getir
                img = ImageClip(img_path, duration=clip_duration + transition_duration)

                # 🔍 Efekt zinciri: önce zoom, sonra çözünürlük
                effects = [
                    Resize(lambda t: 1.0 + zoom_ratio * (t / clip_duration)),  # Zoom
                    Resize(resolution)                                         # Çözünürlük
                ]

                # 🎞️ Geçiş efekti sadece ilk klipten sonrakilere uygulanır
                # İlk klip dışındakilere CrossFadeIn ekleniyor
                if idx != 0:
                    effects.append(CrossFadeIn(transition_duration))

                img = img.with_effects(effects)

                clips.append(img)

            except Exception as e:
                logger.error(f"⚠️ Error with image {img_path}: {e}")
                return None
            
        print("🧩 Concatenating image clips with crossfade")
        video = concatenate_videoclips(clips, method="compose", padding=-transition_duration)
        video = video.with_audio(final_audio)

        # Subtitles
        if srt_path and os.path.isfile(srt_path):
            print(f"💬 Adding subtitles from: {srt_path}")

            with open(srt_path, "r", encoding="utf-8-sig") as f:
                srt_text = f.read()

            subtitles_data = parse_srt(srt_text)
            FONT_PATH = os.path.join(settings.BASE_DIR, "static", "Roboto_Condensed-Bold.ttf")
            def generator(txt):
                return TextClip(
                    text=txt,
                    font_size=92,                # Büyük yazı
                    font=FONT_PATH,          # Kalın font
                    color='white',
                    stroke_color='black',     # Dış hat çizgisi
                    stroke_width=2,           # Çizgi kalınlığı
                    size=(resolution[0] - 100, None),  # Genişlik ekranla uyumlu
                    method='caption',           # Otomatik satır geçişi
                )
            subtitles = SubtitlesClip(subtitles_data, make_textclip=generator)
            video = CompositeVideoClip([video, subtitles.with_position(("center", "center"))])
            video = video.with_audio(final_audio)

        print(f"💾 Writing final video to {output_path}")
        video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        print("✅ Video composition finished successfully")
        return output_path

    except Exception as e:
        logger.exception(f"❌ Failed to compose video: {str(e)}")
        return None
