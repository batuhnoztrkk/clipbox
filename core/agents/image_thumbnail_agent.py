# agents/image_thumbnail_agent.py

from .image_content_agent import ImageContentAgent, ImageContentInput

class ImageThumbnailAgent(ImageContentAgent):
    name: str = "image_thumbnail_generator"
    description: str = (
        "Generates a low-resolution thumbnail or banner image for video covers. "
        "The image must not include text. It is intended for display as a video preview."
    )

