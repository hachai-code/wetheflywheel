"""Step 1 — generate: a topic becomes a validated Guide via a Pydantic AI agent."""
import os
from functools import lru_cache

from models import Guide
from provider import model

MODEL = os.environ.get("GENERATE_MODEL", "openai/gpt-5")

INSTRUCTIONS = (
    "You write for looksmaxxing.guide: evidence-led, harm-reduction-oriented "
    "coverage of male self-improvement for men aged 18-35. Be specific and "
    "honest. Rate every tip's evidence truthfully and never oversell. Put a "
    "harm-reduction note in a section's caution wherever real risk exists. Never "
    "give surgical or prescription-drug advice without a clear see-a-professional "
    "caveat."
)


@lru_cache
def _agent():
    from pydantic_ai import Agent
    return Agent(model(MODEL), output_type=Guide, instructions=INSTRUCTIONS)


def generate(topic, feedback=None) -> Guide:
    prompt = f"Write the looksmaxxing.guide article for the topic: {topic!r}."
    if feedback:
        prompt += ("\n\nA previous draft was rejected by review. Fix these issues:\n"
                   + "\n".join(f"- {item}" for item in feedback))
    return _agent().run_sync(prompt).output
