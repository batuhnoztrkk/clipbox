# core/services/image_generation.py

import openai
import base64
from io import BytesIO
from PIL import Image

def generate_image(user, prompt, size="1024x1024"):
    try:
        api_key = user.api_keys.dalle_api_key
        openai.api_key = api_key

        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size=size,
            response_format="b64_json"
        )

        img_data = base64.b64decode(response['data'][0]['b64_json'])
        return img_data  # Byte data, yazarken kullanılır
    except Exception as e:
        return None
