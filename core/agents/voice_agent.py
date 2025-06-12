from langchain_core.pydantic_v1 import BaseModel, Field
from .base import BaseAgentTool
from typing import Type
import base64
from elevenlabs.client import ElevenLabs

class VoiceAgentInput(BaseModel):
    api_key: str = Field(..., description="ElevenLabs API key to access text-to-speech service")
    text: str = Field(..., description="The input text that will be converted to speech")
    voice_id: str = Field(default="2EiwWnXFnvU5JabPnv8n", description="Voice ID to use (default: Callum)")
    model_id: str = Field(default="eleven_multilingual_v2", description="TTS model ID")

class VoiceAgentOutput(BaseModel):
    audio_base64: str = Field(..., description="The base64-encoded MP3 audio content")

class VoiceAgent(BaseAgentTool):
    name: str = "voice_generator"
    description: str = (
        "Generates MP3 speech from text using ElevenLabs' new SDK. "
        "Defaults to Callum voice. Returns audio as base64-encoded string."
    )
    args_schema: Type[BaseModel] = VoiceAgentInput
    return_schema: Type[BaseModel] = VoiceAgentOutput

    def _run(self, api_key: str, text: str, voice_id: str = "2EiwWnXFnvU5JabPnv8n", model_id: str = "eleven_multilingual_v2") -> dict:
        try:
            client = ElevenLabs(api_key=api_key)

            audio_stream = client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id=model_id,
                output_format="mp3_44100_128",
            )

            audio_bytes = b"".join(audio_stream)  # <-- 🛠️ burada generator'ı bytes'a çeviriyoruz
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

            return VoiceAgentOutput(audio_base64=audio_base64).dict()

        except Exception as e:
            raise RuntimeError(f"Voice generation failed: {str(e)}")