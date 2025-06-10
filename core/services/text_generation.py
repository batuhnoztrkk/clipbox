# core/services/text_generation.py

import openai
from accounts.models import UserAPIKeys

def generate_video_script(user, prompt, duration_minutes=1):
    try:
        api_key = user.api_keys.openai_api_key
        openai.api_key = api_key

        token_estimate = duration_minutes * 150  # ~150 token/dk

        response = openai.ChatCompletion.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=token_estimate,
            temperature=0.8,
        )
        return response.choices[0].message['content']
    except Exception as e:
        return f"Error: {str(e)}"
