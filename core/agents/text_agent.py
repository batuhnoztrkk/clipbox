# agents/text_agent.py
from langchain_openai import ChatOpenAI
from .base import BaseAgentTool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Type
import json, re

class TextAgentOutput(BaseModel):
    title: str = Field(..., description="Suggested title for the video")
    script: str = Field(..., description="The full video script text")
    hashtags: list[str] = Field(..., description="List of relevant and popular hashtags")
    description: str = Field(..., description="Suggested description for the video")
    thumbnail_prompt: str = Field(..., description="AI prompt to generate the video thumbnail")
    content_prompt: str = Field(..., description="AI prompt to generate or enhance video content")

class TextAgentInput(BaseModel):
    api_key: str = Field(..., description="Openai için api key")
    topic_title: str = Field(..., description="Video için başlık")
    prompt_context: str = Field(..., description="Video içeriği hakkında detaylı açıklama")
    duration_minutes: int = Field(1, description="Video süresi (dakika olarak)")
    language: str = Field("tr", description="Video dili")

class TextAgent(BaseAgentTool):
    name: str = "text_generator"
    description: str = (
        "Creates a full social video content pack (title, script, description, hashtags, and AI prompts) "
        "based on a given topic. Optimized for platforms like TikTok, Reels, Shorts. "
        "Ensures the generated script matches the specified language exactly and is suitable for voice-over, "
        "lasting slightly less than the specified duration (max 5 seconds shorter). "
        "It avoids any markdown, explanations, or code blocks — returns only valid JSON."
    )
    args_schema: Type[BaseModel] = TextAgentInput
    return_schema: Type[BaseModel] = TextAgentOutput

    def _run(self, api_key: str, topic_title: str, prompt_context: str, language: str, duration_minutes: int = 1) -> dict:
        prompt = (
            "You are an AI backend agent. You NEVER respond with markdown, explanations, or code blocks.\n\n"
            "You are a professional scriptwriter for TikTok, Instagram Reels, and YouTube Shorts.\n"
            "Your task is to write a high-impact, curiosity-driven, emotionally engaging script.\n"
            "Requirements:\n"
            "- Grab attention in the first 3 seconds.\n"
            "- Use short, punchy sentences.\n"
            "- Do NOT include production directions or closing remarks.\n"
            "- Do NOT use markdown or code blocks.\n"
            "- End with a twist, a question, or something thought-provoking.\n\n"
            "Strict rules:\n"
            "- All output must be in the exact language: **{language}**\n"
            "- The script must be suitable for narration and should last NO MORE than {duration_minutes * 60 - 5} seconds when read aloud.\n"
            "- Estimate 2.5 words per second when writing.\n\n"
            "Inputs:\n"
            f"- Title: {topic_title}\n"
            f"- Context: {prompt_context}\n"
            f"- Duration: {duration_minutes} minute(s)\n"
            f"- Language: {language}\n\n"
            "Output ONLY a JSON object with the following keys:\n"
            "title (string), script (string), hashtags (array of strings), description (string), "
            "thumbnail_prompt (string), content_prompt (string)"
        )

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.8, api_key=api_key)
        raw_response = llm.invoke(prompt).content

        # Remove code block if it accidentally adds it
        raw_json = re.sub(r"^```json|```$", "", raw_response.strip())

        try:
            parsed = json.loads(raw_json)
            return TextAgentOutput(**parsed).dict()
        except Exception as e:
            raise ValueError(f"Failed to parse model response: {e}\nRaw response:\n{raw_response}")