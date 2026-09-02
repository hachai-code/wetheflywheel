"""Step 2 — validate: a Pydantic AI agent reviews the guide. Returns a Report.

Structural validity is now guaranteed by Pydantic (a Guide is already valid), so
this step is purely the editorial/safety gate. use_model=False keeps it offline
(used by --demo and the sample-driven UI).
"""
import os
from functools import lru_cache

from models import Guide, Report

MODEL = os.environ.get("VALIDATE_MODEL", "openai/gpt-5-mini")

RUBRIC = (
    "You are the editorial safety reviewer for looksmaxxing.guide. Review the "
    "guide and return a report. Raise a 'blocker' for: advice that could cause "
    "harm without a caveat (surgery, prescription/off-label drugs, aggressive "
    "DIY), evidence levels that oversell (e.g. calling an anecdotal claim "
    "'strong'), or medical claims that need a professional referral and lack one. "
    "Raise a 'warning' for thin sections, vague tips, or a missing harm-reduction "
    "caution where one is warranted. If nothing is wrong, return passed=true with "
    "no issues."
)


@lru_cache
def _agent():
    from pydantic_ai import Agent
    from provider import model
    return Agent(model(MODEL), output_type=Report, instructions=RUBRIC)


def validate(guide: Guide, use_model: bool = True) -> Report:
    if not use_model:
        return Report(passed=True, issues=[])
    return _agent().run_sync(guide.model_dump_json()).output
