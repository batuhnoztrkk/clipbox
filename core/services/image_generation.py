# core/services/image_generation.py
from openai import OpenAI
import base64

def generate_image(user, prompt, size="1024x1024"):
    try:
        api_key = user.api_keys.dalle_api_key
        client = OpenAI(api_key=api_key)

        response = client.images.generate(
            prompt=prompt,
            n=1,
            size=size,
            response_format="b64_json"
        )

        img_data = base64.b64decode(response.data[0].b64_json)
        return img_data  # Byte data, yazarken kullanılır
    except Exception as e:
        return None
