from openai import OpenAI

def generate_voice(user, text, voice="alloy"):
    try:
        api_key = user.api_keys.tts_api_key
        client = OpenAI(api_key=api_key)

        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        return response.content  # MP3 binary
    except Exception as e:
        return None