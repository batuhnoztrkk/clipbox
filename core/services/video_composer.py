import logging
from moviepy import (
    ImageClip,
    concatenate_videoclips,
    AudioFileClip,
    CompositeAudioClip,
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
)
from moviepy.video.fx.Resize import Resize
from moviepy.video.tools.subtitles import SubtitlesClip
import os
import logging
import re

logger = logging.getLogger(__name__)

def parse_srt(srt_text):
    subtitles = []
    entries = re.split(r'\n\s*\n', srt_text.strip())

    for entry in entries:
        lines = entry.strip().split("\n")
        if len(lines) >= 3:
            # Zaman bilgisi
            time_line = lines[1]
            start_str, end_str = time_line.split(" --> ")

            def time_to_seconds(t):
                h, m, s = re.split(r'[:,]', t)
                return int(h) * 3600 + int(m) * 60 + float(s.replace(',', '.'))

            start = time_to_seconds(start_str)
            end = time_to_seconds(end_str)

            # Metin kısmı
            text = " ".join(lines[2:])
            subtitles.append(((start, end), text))

    return subtitles


def compose_video(
    images,
    audio_path,
    output_path="output.mp4",
    music_path=None,
    resolution=(1280, 720),  # (width, height) örn: 1280x720
    srt_path=None,
):
    print("Starting video composition")
    try:
        if not images:
            print("No images provided to compose_video")
            return None

        print(f"Video resolution set to: {resolution[0]}x{resolution[1]}")

        # Ana ses klibi
        print(f"Loading main audio from {audio_path}")
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        print(f"Audio duration: {audio_duration:.2f} seconds")

        # Arka plan müziği varsa
        if music_path:
            print(f"Loading background music from {music_path}")
            music = AudioFileClip(music_path).volumex(0.3)
            final_audio = CompositeAudioClip([audio, music])
            # Süre final_audio'nun süresi ana sesin süresiyle aynı olacak şekilde ayarlanmalı
            final_audio = final_audio.set_duration(audio_duration)
        else:
            final_audio = audio

        # Resimlerin her birinin gösterim süresi
        clip_duration = audio_duration / len(images)
        print(f"Each image will be shown for: {clip_duration:.2f} seconds")

        clips = []
        for idx, img_path in enumerate(images):
            print(f"Adding image {idx + 1}/{len(images)} to video: {img_path}")

            try:
                # Resmi video çözünürlüğüne göre boyutlandırıyoruz
                clip = ImageClip(img_path,  duration=clip_duration)
                # İlk resize sabit çözünürlük için
                clip = clip.with_effects([Resize(resolution)])

                # Zoom efekti için zamanla değişen resize
                zoom_start = 1
                zoom_end = 1.05
                zoom_func = lambda t: zoom_start + (zoom_end - zoom_start) * (t / clip_duration)

                clip = clip.with_effects([Resize(zoom_func)])
                clips.append(clip)
            except Exception as e:
                print(f"Error creating ImageClip for image {img_path}: {e}")
                return None

        print("Concatenating video clips")
        video = concatenate_videoclips(clips, method="compose")
        print("Adding final audio")
        video.audio = final_audio

        # Altyazı varsa ekle
        if srt_path and os.path.isfile(srt_path):
            print(f"Adding subtitles from {srt_path}")

            def subtitle_generator(txt):
                # Basit beyaz metin
                return TextClip(txt, fontsize=24, color='white', font='Arial', stroke_color='black', stroke_width=0.5)

            with open(srt_path, "r", encoding="utf-8") as f:
                srt_text = f.read()

            try:
                subtitles_data = parse_srt(srt_text)
                subtitles = SubtitlesClip(subtitles_data, subtitle_generator)
                video = CompositeVideoClip([video, subtitles.set_pos(("center", "bottom"))])
            except Exception as e:
                print(f"Failed to add subtitles: {e}")
        else:
            if srt_path:
                print(f"Subtitle file {srt_path} not found, skipping subtitles.")

        print(f"Writing final video file to {output_path}")
        video.write_videofile(output_path, fps=24)

        print("Video composition finished successfully")
        return output_path
    except Exception as e:
        print(f"Failed to compose video: {e}")
        return None
