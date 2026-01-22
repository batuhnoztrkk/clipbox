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
    CompositeVideoClip
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

def animated_textclip(txt, start, end, resolution, font_path):
    """
    Harf harf altyazı efekti oluşturur (moving letter effect).
    """
    duration = end - start
    total_chars = len(txt)
    clips = []

    for i in range(1, total_chars + 1):
        sub_txt = txt[:i]

        try:
            clip = (
                TextClip(
                    text=sub_txt,
                    font=font_path,
                    font_size=92,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    size=(resolution[0] - 100, None),
                    method="caption"
                )
                .with_position(("center", "center"))
                .with_start(start + ((i - 1) * (duration / total_chars)))
                .with_duration(duration / total_chars)
            )

            clips.append(clip)
        except Exception as e:
            print(f"❌ Error creating animated subtitle for: '{sub_txt}' -> {e}")
            continue

    return CompositeVideoClip(clips).with_start(start).with_duration(duration)

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
        # Subtitles
        if srt_path and os.path.isfile(srt_path):
            print(f"💬 Adding subtitles from: {srt_path}")

            with open(srt_path, "r", encoding="utf-8-sig") as f:
                srt_text = f.read()

            subtitles_data = parse_srt(srt_text)
            animated_subs = []
            FONT_PATH = os.path.join(settings.BASE_DIR, "static", "Roboto_Condensed-Bold.ttf")

            for (start, end), text in subtitles_data:
                animated = animated_textclip(text, start, end, resolution, FONT_PATH)
                animated_subs.append(animated)

            subtitle_layer = CompositeVideoClip(animated_subs)
            video = CompositeVideoClip([video, subtitle_layer])
            video = video.with_audio(final_audio)


        print(f"💾 Writing final video to {output_path}")
        video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        print("✅ Video composition finished successfully")
        return output_path

    except Exception as e:
        logger.exception(f"❌ Failed to compose video: {str(e)}")
        return None
