# core/services/subtitle_generator.py

from faster_whisper import WhisperModel

def format_timestamp(seconds: float) -> str:
    """SRT biçiminde timestamp üretir."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"

def generate_subtitles_with_whisper(audio_path: str, model_size: str = "medium") -> str:
    """
    Verilen ses dosyasını Whisper ile işleyerek zaman kodlu SRT döner.

    Args:
        audio_path (str): MP3/WAV gibi ses dosyasının tam yolu
        model_size (str): Whisper modeli (tiny, base, small, medium, large)

    Returns:
        str: .srt içeriği (string olarak)
    """
    model = WhisperModel(model_size, device="cpu")  # GPU varsa "cuda" yaz
    segments, info = model.transcribe(audio_path, beam_size=5)

    srt_output = ""
    for idx, segment in enumerate(segments, start=1):
        start = format_timestamp(segment.start)
        end = format_timestamp(segment.end)
        text = segment.text.strip()

        srt_output += f"{idx}\n{start} --> {end}\n{text}\n\n"

    return srt_output