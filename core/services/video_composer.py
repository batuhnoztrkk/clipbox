# core/services/video_composer.py

from moviepy.editor import *

def compose_video(images, audio_path, music_path=None, output_path="output.mp4"):
    try:
        clips = [ImageClip(img).set_duration(5) for img in images]
        video = concatenate_videoclips(clips, method="compose")

        audio = AudioFileClip(audio_path)

        if music_path:
            music = AudioFileClip(music_path).volumex(0.3)
            final_audio = CompositeAudioClip([audio, music])
        else:
            final_audio = audio

        video = video.set_audio(final_audio)
        video.write_videofile(output_path, fps=24)

        return output_path
    except Exception as e:
        return None
