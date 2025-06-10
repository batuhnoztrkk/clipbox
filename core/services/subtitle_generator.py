# core/services/subtitle_generator.py

def generate_subtitles_simple(text, duration_seconds=60):
    """
    Verilen metni sabit süreli bloklara bölerek SRT formatında altyazı oluşturur.

    Args:
        text (str): Tam metin
        duration_seconds (int): Toplam ses uzunluğu (saniye)

    Returns:
        str: .srt içeriği (string olarak)
    """
    lines = [line.strip() for line in text.split(".") if line.strip()]
    total_lines = len(lines)
    if total_lines == 0:
        return ""

    segment_duration = duration_seconds // total_lines

    def format_time(seconds):
        mins, secs = divmod(seconds, 60)
        hrs, mins = divmod(mins, 60)
        return f"{hrs:02}:{mins:02}:{secs:02},000"

    srt_content = ""
    for i, line in enumerate(lines):
        start_sec = i * segment_duration
        end_sec = (i + 1) * segment_duration
        srt_content += f"{i + 1}\n"
        srt_content += f"{format_time(start_sec)} --> {format_time(end_sec)}\n"
        srt_content += f"{line.strip()}\n\n"

    return srt_content

# import os
# import tempfile
# from aeneas.executetask import ExecuteTask
# from aeneas.task import Task

# def generate_subtitles(text, audio_path, output_srt_path):
#     try:
#         # Temp TXT dosyası oluştur
#         with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
#             f.write(text)
#             text_path = f.name

#         config_string = u"task_language=eng|is_text_type=plain|os_task_file_format=srt"
#         task = Task(config_string=config_string)
#         task.audio_file_path_absolute = audio_path
#         task.text_file_path_absolute = text_path
#         task.sync_map_file_path_absolute = output_srt_path

#         ExecuteTask(task).execute()
#         task.output_sync_map_file()

#         os.remove(text_path)
#         return output_srt_path
#     except Exception as e:
#         print("Subtitle generation error:", e)
#         return None