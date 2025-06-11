from core.agents.text_agent import TextAgent

def call_text_agent(user, topic_title, prompt_context, duration_minutes):
    # Burada API key vs user bazlı alınabilir
    api_key = user.api_keys.openai_api_key

    text_agent = TextAgent()
    result = text_agent._run(
        api_key=api_key,
        topic_title=topic_title,
        prompt_context=prompt_context,
        duration_minutes=duration_minutes
    )
    return result
