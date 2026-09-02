"""Step 1 — generate: a topic string becomes structured guide JSON via OpenRouter."""
import os

from client import structured
from schema import GUIDE_SCHEMA

MODEL = os.environ.get("GENERATE_MODEL", "openai/gpt-5")

SYSTEM = (
    "You write for looksmaxxing.guide: evidence-led, harm-reduction-oriented "
    "coverage of male self-improvement for men aged 18-35. Be specific and "
    "honest. Rate every tip's evidence (strong/moderate/limited/anecdotal) "
    "truthfully and never oversell. Put a harm-reduction note in a section's "
    "caution wherever real risk exists. Never give surgical or prescription-drug "
    "advice without a clear see-a-professional caveat."
)


def generate(topic, feedback=None):
    user = f"Write the looksmaxxing.guide article for the topic: {topic!r}."
    if feedback:
        user += ("\n\nA previous draft was rejected by review. Fix these issues:\n"
                 + "\n".join(f"- {item}" for item in feedback))
    return structured(
        MODEL, "guide", GUIDE_SCHEMA,
        [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
    )
