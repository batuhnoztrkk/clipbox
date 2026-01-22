# clipbox

A Django-based toolkit for generating short-form videos using AI-assisted content creation:
- Generate scripts and metadata
- Convert text to speech (OpenAI TTS)
- Generate subtitles (Whisper / faster-whisper)
- Compose final videos from images, audio and animated subtitles (moviepy + ffmpeg)

This README guides you through setup, running, and basic developer usage.

---

## Table of Contents

- Project Overview
- Features
- Requirements
- Quickstart (Local Development)
- Configuration & Environment Variables
- Running the App
- Using the app
  - Web UI
  - Programmatic endpoints
  - Django shell examples (video composition, subtitles, TTS)
- Important modules & project layout
- Testing
- Troubleshooting & Tips
- Contributing
- License

---

## Project Overview

clipbox is a Django application designed to automate creation of short/long videos by combining:
- AI-generated scripts and metadata
- Text-to-speech audio generation
- Image assets (content & thumbnails)
- Subtitle generation (SRT) and animated subtitle rendering
- Final composition using moviepy/ffmpeg

Typical flow:
1. Create a Panel (workspace)
2. Create a Video record (title, duration, type)
3. Run generation steps (text → voice → subtitle → image assets → compose final video)

---

## Features

- Panel-based organization of content and generation settings
- Video model with status tracking and media fields (voice, subtitles, images, thumbnail, final video)
- Subtitle generation using Whisper (via faster-whisper)
- Text-to-speech with OpenAI TTS (openai package)
- Video composition using moviepy (zoom, crossfade, animated subtitles)
- Simple endpoints to trigger generation steps (backend handles the orchestration)

---

## Requirements

System:
- Python 3.10+ (project uses modern Python tooling)
- ffmpeg installed and available on PATH (moviepy relies on ffmpeg)
  - On macOS (Homebrew): brew install ffmpeg
  - On Ubuntu/Debian: sudo apt update && sudo apt install -y ffmpeg
- Sufficient disk space for media files
- (Optional) CUDA-capable GPU and proper drivers for large Whisper models — otherwise CPU-only is supported

Python packages (included in repository):
- See `requirements.txt`
- Notable packages: Django 5.2.3, moviepy, ffmpeg-python, openai, faster-whisper (may need to be added manually)

Important: `faster-whisper` is used by the code (core/services/subtitle_generator.py). If not present in `requirements.txt`, install it manually:
pip install faster-whisper

---

## Quickstart — Local Development

1. Clone repository
   ```
   git clone https://github.com/batuhnoztrkk/clipbox.git
   cd clipbox
   ```

2. Create & activate a virtual environment (recommended)
   ```
   python -m venv .venv
   source .venv/bin/activate    # macOS / Linux
   .venv\Scripts\activate       # Windows (PowerShell)
   ```

3. Install Python dependencies
   ```
   pip install -r requirements.txt
   # If `faster-whisper` is missing, then:
   pip install faster-whisper
   ```

4. Apply database migrations
   ```
   python manage.py migrate
   ```

5. Create a superuser (for admin / quick access)
   ```
   python manage.py createsuperuser
   ```

6. (Optional) Collect static files for production-like behaviour
   ```
   python manage.py collectstatic
   ```

7. Run the development server
   ```
   python manage.py runserver
   ```

Open your browser:
- Root URL `/` redirects to `/panel/` for authenticated users or `/accounts/login/` otherwise
- Admin: `/admin/`

---

## Configuration & Environment Variables

The project contains a default SECRET_KEY in settings for development. For production, override with environment variables and set DEBUG=False.

Recommended environment variables:
- DJANGO_SECRET_KEY (or set SECRET_KEY in environment / your deployment)
- OPENAI_API_KEY — required if you use the OpenAI TTS agent
- WHISPER_MODEL_SIZE — optional (tiny, base, small, medium, large) when calling the subtitle generator
- DJANGO_ALLOWED_HOSTS — set ALLOWED_HOSTS in production

Example .env (use python-dotenv or set OS env vars):
```
OPENAI_API_KEY=sk-...
DJANGO_SECRET_KEY=your-production-secret
WHISPER_MODEL_SIZE=medium
```

Note: settings.py currently embeds SECRET_KEY and DEBUG=True for local development. Update these for production.

Media & static:
- MEDIA_ROOT: media/
- STATIC_ROOT: static/
- An included font used for subtitle rendering: staticfiles/Roboto_Condensed-Bold.ttf

---

## Running & Usage

Run the server:
```
python manage.py runserver
```

Create content (via UI):
1. Log in or register (accounts app).
2. Create a Panel in the UI.
3. Create a Video under a Panel.
4. Use the UI to trigger generation steps (the project contains JS/UI forms and backend endpoints that handle content creation).

Programmatic API (generation endpoint):
- videos.views.generate_content is a POST endpoint guarded with @login_required and @csrf_exempt.
- Steps accepted: `text`, `voice`, `subtitle`, `content_images`, `banner_image`, `thumbnail_image`, `edit`
- Example (conceptual): POST to `/videos/generate/<video_id>/<step>/` with an authenticated session to trigger that step.

Because the endpoint requires authentication, use one of:
- Log in via the web UI and make AJAX calls from the browser.
- Use `curl` with session cookies (after logging in).
- Use the Django shell to call the underlying utility functions directly (recommended for testing).

---

## Developer Examples (Django shell)

Open a Django shell:
```
python manage.py shell
```

1) Generate subtitles with Whisper (faster-whisper)
```py
from core.services.subtitle_generator import generate_subtitles_with_whisper
srt_text = generate_subtitles_with_whisper("media/voices/my_audio.mp3", model_size="small")
print(srt_text)
# You can save:
open("media/subtitles/generated.srt", "w", encoding="utf-8").write(srt_text)
```

2) Compose a video using moviepy helper
```py
from core.services.video_composer import compose_video
images = ["media/video_images/1.jpg", "media/video_images/2.jpg"]
audio = "media/voices/tts.mp3"
srt = "media/subtitles/generated.srt"   # optional
out = "media/final_videos/final_output.mp4"
compose_video(images, audio, output_path=out, resolution=(1280,720), srt_path=srt)
```

3) Use the OpenAI voice agent (direct openai usage recommended)
```py
# Example direct usage with openai package (project includes an agent class)
import openai, base64
openai.api_key = "sk-..."
resp = openai.audio.speech.create(model="gpt-4o-mini-tts", input="Hello", voice="alloy", response_format="mp3")
with open("media/voices/tts.mp3", "wb") as f:
    f.write(resp.content)
```

4) Call generation utilities from `videos.utils` (used by views)
```py
# Example (run inside manage.py shell)
from django.contrib.auth.models import User
from videos.models import Video
from videos.utils import generate_text_content_util

user = User.objects.first()
video = Video.objects.first()
result = generate_text_content_util(user, video)
print(result)
```
(Adjust imports if utility functions require additional arguments; inspect `videos/utils.py`.)

---

## Important Modules & Project Layout

- clipbox/  - Django project settings & URL routing
  - settings.py - DB, static/media, installed apps, templates
  - urls.py - top-level routes: admin/, accounts/, videos/, panel/
- accounts/ - authentication / registration (templates present)
- panels/ - Panel model, UI for user workspaces
  - models.py: Panel (workspace settings, ad/outro/defaults)
- videos/ - Video model, views & templates
  - models.py: Video, VideoAIContent, VideoImage
  - views.py: list/create/detail/edit, generate_content POST endpoint
  - utils.py: helper utilities used by the view (generate_*_util)
- core/ - services & AI agents
  - services/video_composer.py - compose_video(images, audio_path, output_path, music_path, resolution, srt_path)
  - services/subtitle_generator.py - generate_subtitles_with_whisper(audio_path, model_size)
  - agents/voice_agent_openai.py - wrapper for OpenAI TTS flow (needs OPENAI API key)

---

## Testing

Run Django tests:
```
python manage.py test
```

The repository includes test modules (accounts/tests.py, panels/tests.py, videos/tests.py, core/tests.py). Adjust or expand tests when adding new features.

---

## Troubleshooting & Tips

- ffmpeg errors:
  - Ensure ffmpeg is installed and on PATH. moviepy will raise errors when ffmpeg is missing.
  - Verify by running `ffmpeg -version`.

- Performance:
  - Whisper models (medium/large) can be slow on CPU. Use smaller models or run on GPU for faster subtitle generation.
  - Generation steps can create large temporary files; monitor disk space.

- Missing faster-whisper:
  - The project imports `WhisperModel` from `faster_whisper`. If you get ModuleNotFoundError, install it:
    ```
    pip install faster-whisper
    ```

- Font & subtitle rendering:
  - The video composer references `static/Roboto_Condensed-Bold.ttf` for subtitle fonts. Ensure the font file is present in `static/` or update FONT_PATH in `core/services/video_composer.py`.

- OpenAI TTS:
  - Ensure `OPENAI_API_KEY` is valid. OpenAI TTS models may change; check the OpenAI SDK and update parameters as needed.

- Security:
  - Do not commit production secrets. Move SECRET_KEY and API keys to env vars or secret management.
  - Turn off DEBUG and set ALLOWED_HOSTS in production.

---

## Contribution

Contributions welcome. Suggested workflow:
1. Fork the repo
2. Create a feature branch
3. Add tests for new behavior
4. Open a pull request with a clear description and testing steps

Please follow typical GitHub PR etiquette.

---
