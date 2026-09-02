"""OpenRouter access shared by the agent steps.

OpenRouter speaks the OpenAI API, so we point the OpenAI SDK at it and ask for
JSON with response_format. Docs: https://openrouter.ai/docs/features/structured-outputs
"""
import json
import os

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Get a key at "
                "https://openrouter.ai/keys, or run the pipeline with --demo."
            )
        from openai import OpenAI  # lazy: --demo runs with no deps installed
        _client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    return _client


def structured(model, schema_name, schema, messages):
    """Call `model` and return parsed JSON conforming to `schema`."""
    completion = _get_client().chat.completions.create(
        model=model,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        },
    )
    return json.loads(completion.choices[0].message.content)
