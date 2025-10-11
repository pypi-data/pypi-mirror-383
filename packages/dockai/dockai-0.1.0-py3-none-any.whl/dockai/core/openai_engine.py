import os
from openai import OpenAI

def analyze_with_openai(log_text):
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY is not set in environment variables.")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a DevOps AI assistant."},
            {"role": "user", "content": log_text}
        ]
    )
    return response.choices[0].message.content
