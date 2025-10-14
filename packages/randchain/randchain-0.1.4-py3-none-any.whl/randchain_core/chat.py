from typing import Any


def ollama_chat(prompt: str, model_id: str, query: Any, messages: list = []):
    import ollama
    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": query})
    response = ollama.chat(
        model=model_id,
        messages=messages
    )
    return response["message"]["content"]

def open_ai_chat(api_key: str, prompt: str, model_id: str, query: Any, messages: list = []):
    import openai
    client = openai.OpenAI(api_key=api_key)
    messages.append({"role": "system", "content": prompt})
    messages.append({"role": "user", "content": query})
    response = client.chat.completions.create(
        model=model_id,
        messages=messages
    )
    return response.choices[0].message.content