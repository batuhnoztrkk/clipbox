# agents/voice_agent.py

from langchain_core.pydantic_v1 import BaseModel
from .base import BaseAgentTool
from typing import Type
import base64
import openai
from langchain_core.pydantic_v1 import BaseModel, Field

class VoiceAgentInput(BaseModel):
    api_key: str = Field(..., description="OpenAI API key to access text-to-speech endpoint")
    text: str = Field(..., description="The input text that will be converted to speech")
    voice: str = Field(default="alloy", description="The desired voice: alloy, echo, fable, onyx, nova, shimmer")

class VoiceAgentOutput(BaseModel):
    audio_base64: str = Field(..., description="The base64-encoded MP3 audio content generated from the text")

class VoiceAgent(BaseAgentTool):
    name: str = "voice_generator"
    description: str = (
        "Converts input text into MP3 speech using OpenAI's TTS model. "
        "Accepts a voice type and returns a base64-encoded MP3 binary string."
    )
    args_schema: Type[BaseModel] = VoiceAgentInput
    return_schema: Type[BaseModel] = VoiceAgentOutput

    def _run(self, api_key: str, text: str, voice: str = "alloy") -> dict:
        openai.api_key = api_key

        try:
            response = openai.audio.speech.create(
                model="gpt-4o-mini-tts",
                input=text,
                voice=voice,
                response_format="mp3"
            )

            audio_base64 = base64.b64encode(response.content).decode("utf-8")
            return VoiceAgentOutput(audio_base64=audio_base64).dict()

        except Exception as e:
            raise RuntimeError(f"Voice generation failed: {str(e)}")