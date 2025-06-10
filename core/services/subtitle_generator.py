# core/services/subtitle_generator.py

import os
import tempfile
from aeneas.executetask import ExecuteTask
from aeneas.task import Task

def generate_subtitles(text, audio_path, output_srt_path):
    try:
        # Temp TXT dosyası oluştur
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt") as f:
            f.write(text)
            text_path = f.name

        config_string = u"task_language=eng|is_text_type=plain|os_task_file_format=srt"
        task = Task(config_string=config_string)
        task.audio_file_path_absolute = audio_path
        task.text_file_path_absolute = text_path
        task.sync_map_file_path_absolute = output_srt_path

        ExecuteTask(task).execute()
        task.output_sync_map_file()

        os.remove(text_path)
        return output_srt_path
    except Exception as e:
        print("Subtitle generation error:", e)
        return None
