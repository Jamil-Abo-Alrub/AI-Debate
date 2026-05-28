import os
from typing import Dict, Iterator, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client: Optional[OpenAI] = None


def client() -> OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not set. Copy .env.example to .env and fill it in.")
        _client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    return _client


def stream_chat(messages: List[Dict], model: str = "deepseek-chat", temperature: float = 0.85) -> Iterator[str]:
    response = client().chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    for chunk in response:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def chat(
    messages: List[Dict],
    model: str = "deepseek-chat",
    temperature: float = 0.3,
    response_format: Optional[Dict] = None,
) -> str:
    kwargs: Dict = {"model": model, "messages": messages, "temperature": temperature}
    if response_format is not None:
        kwargs["response_format"] = response_format
    return client().chat.completions.create(**kwargs).choices[0].message.content
