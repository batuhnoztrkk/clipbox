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

class TextAgent(BaseAgentTool):
    name: str = "text_generator"
    description: str = (
        "Generates a complete social media video content package including title, script, hashtags, "
        "and a short description, based on a topic and context. Designed for TikTok, Reels, and Shorts."
    )
    args_schema: Type[BaseModel] = TextAgentInput
    return_schema: Type[BaseModel] = TextAgentOutput

    def _run(self, api_key: str, topic_title: str, prompt_context: str, duration_minutes: int = 1) -> dict:
        prompt = (
            "You are a professional viral video scriptwriter for TikTok, Instagram Reels, and YouTube Shorts. "
            "Write a highly engaging, curiosity-driven, emotional video script that grabs attention in the first 3 seconds "
            "with short, punchy sentences. The script should be suitable for narration, without describing video production or ending lines. "
            "Make the story mysterious, shocking or emotionally powerful. End with a twist or question that hooks the viewer. "
            "\n\n"
            "Input:\n"
            f"- Title: {topic_title}\n"
            f"- Context: {prompt_context}\n"
            f"- Duration: {duration_minutes} minute(s)\n\n"
            "Output strictly as JSON with these keys:\n"
            "title (string), script (string), hashtags (array of strings), description (string), "
            "thumbnail_prompt (string), content_prompt (string)\n\n"
            "Do NOT include explanations or instructions. DO NOT mention 'video ends' or similar. "
            "JUST return the JSON object."
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