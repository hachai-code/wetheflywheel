"""The shared OpenRouter model for the Pydantic AI agents.

OpenRouter is OpenAI-compatible, so we use OpenAIChatModel + OpenAIProvider with
OpenRouter's base_url. pydantic_ai is imported lazily so the offline --demo path
(which never builds a model) runs without it installed.
"""
import os
from functools import lru_cache


@lru_cache
def model(slug):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Get a key at "
            "https://openrouter.ai/keys, or run the pipeline with --demo."
        )
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider

    return OpenAIChatModel(
        slug,
        provider=OpenAIProvider(
            base_url="https://openrouter.ai/api/v1", api_key=api_key
        ),
    )
