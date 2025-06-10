# core/services/voice_generation.py

import openai

def generate_voice(user, text, voice="alloy"):
    try:
        api_key = user.api_keys.tts_api_key
        openai.api_key = api_key

        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        return response.content  # MP3 binary
    except Exception as e:
        return None
