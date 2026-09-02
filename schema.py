"""JSON schemas shared across the pipeline.

One guide schema, two consumers: generate.py sends GUIDE_SCHEMA as the model's
response_format, and validate.py checks generated JSON against it before the
model rubric pass runs. REPORT_SCHEMA shapes the validator's verdict.
"""

EVIDENCE = ["strong", "moderate", "limited", "anecdotal"]
RATINGS = ["low", "medium", "high"]

_TIP = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "claim": {"type": "string"},
        "detail": {"type": "string"},
        "evidence": {"type": "string", "enum": EVIDENCE},
        "effort": {"type": "string", "enum": RATINGS},
        "impact": {"type": "string", "enum": RATINGS},
    },
    "required": ["claim", "detail", "evidence", "effort", "impact"],
}

_SECTION = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "heading": {"type": "string"},
        "body": {"type": "string"},
        "tips": {"type": "array", "items": _TIP},
        "caution": {"type": ["string", "null"]},
    },
    "required": ["heading", "body", "tips", "caution"],
}

GUIDE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "topic": {"type": "string"},
        "title": {"type": "string"},
        "dek": {"type": "string"},
        "updated": {"type": "string"},
        "reading_time_min": {"type": "integer"},
        "bottom_line": {"type": "array", "items": {"type": "string"}},
        "sections": {"type": "array", "items": _SECTION},
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "label": {"type": "string"},
                    "note": {"type": "string"},
                },
                "required": ["label", "note"],
            },
        },
    },
    "required": ["topic", "title", "dek", "updated", "reading_time_min",
                 "bottom_line", "sections", "sources"],
}

REPORT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "passed": {"type": "boolean"},
        "issues": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "severity": {"type": "string", "enum": ["blocker", "warning"]},
                    "where": {"type": "string"},
                    "message": {"type": "string"},
                },
                "required": ["severity", "where", "message"],
            },
        },
    },
    "required": ["passed", "issues"],
}
