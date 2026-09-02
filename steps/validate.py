"""Step 2 — validate: a code-side schema check plus a model rubric pass.

The gate. Returns {"passed": bool, "issues": [...]}. Schema errors short-circuit
before any model call; use_model=False keeps the whole step offline (--demo).
"""
import json
import os

from client import structured
from schema import EVIDENCE, GUIDE_SCHEMA, RATINGS, REPORT_SCHEMA

MODEL = os.environ.get("VALIDATE_MODEL", "openai/gpt-5-mini")

RUBRIC = (
    "You are the editorial safety reviewer for looksmaxxing.guide. Review the "
    "guide JSON and return a report. Raise a 'blocker' for: advice that could "
    "cause harm without a caveat (surgery, prescription/off-label drugs, "
    "aggressive DIY), evidence levels that oversell (e.g. calling an anecdotal "
    "claim 'strong'), or medical claims that need a professional referral and "
    "lack one. Raise a 'warning' for thin sections, vague tips, or a missing "
    "harm-reduction caution where one is warranted. If nothing is wrong, return "
    "passed=true with an empty issues list."
)


def _schema_errors(guide):
    """Minimal structural check (no jsonschema dependency): required keys + enums."""
    errors = []
    for key in GUIDE_SCHEMA["required"]:
        if key not in guide:
            errors.append(f"missing required field: {key}")
    for si, section in enumerate(guide.get("sections", [])):
        for ti, tip in enumerate(section.get("tips", [])):
            where = f"sections[{si}].tips[{ti}]"
            if tip.get("evidence") not in EVIDENCE:
                errors.append(f"{where}.evidence not one of {EVIDENCE}")
            if tip.get("effort") not in RATINGS:
                errors.append(f"{where}.effort not one of {RATINGS}")
            if tip.get("impact") not in RATINGS:
                errors.append(f"{where}.impact not one of {RATINGS}")
    return errors


def validate(guide, use_model=True):
    errors = _schema_errors(guide)
    if errors:
        return {"passed": False,
                "issues": [{"severity": "blocker", "where": "schema", "message": m}
                           for m in errors]}
    if not use_model:
        return {"passed": True, "issues": []}
    return structured(
        MODEL, "review", REPORT_SCHEMA,
        [{"role": "system", "content": RUBRIC},
         {"role": "user", "content": json.dumps(guide, ensure_ascii=False)}],
    )
