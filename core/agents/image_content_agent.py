# agents/image_content_agent.py
from langchain_core.pydantic_v1 import BaseModel
from .base import BaseAgentTool
from typing import Type
import openai
import base64
from langchain_core.pydantic_v1 import BaseModel, Field

class ImageContentInput(BaseModel):
    api_key: str = Field(..., description="OpenAI API key for image generation")
    prompt: str = Field(..., description="Text prompt describing the image to be generated")
    size: str = Field(default="1024x1024", description="Image size in format WxH, e.g., 1024x1024")

class ImageContentOutput(BaseModel):
    image_base64: str = Field(..., description="Base64-encoded image content (PNG)")

class ImageContentAgent(BaseAgentTool):
    name: str = "image_content_generator"
    description: str = (
        "Generates high-quality, AI-based images that visually represent video content. "
        "The image should not contain any text. It is ideal for supporting video visuals."
    )
    args_schema: Type[BaseModel] = ImageContentInput
    return_schema: Type[BaseModel] = ImageContentOutput

    def _run(self, api_key: str, prompt: str, size: str = "1024x1024") -> dict:
        openai.api_key = api_key

        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size=size,
                response_format="b64_json"
            )
            image_base64 = response["data"][0]["b64_json"]
            return ImageContentOutput(image_base64=image_base64).dict()

        except Exception as e:
            raise RuntimeError(f"Image generation failed: {str(e)}")