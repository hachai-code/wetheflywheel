"""Pydantic models for a looksmaxxing.guide article and the review report.

These replace hand-written JSON schemas: Pydantic AI derives each agent's
structured-output schema from them, and the same classes validate loaded JSON.
"""
from typing import Literal

from pydantic import BaseModel, Field

Evidence = Literal["strong", "moderate", "limited", "anecdotal"]
Rating = Literal["low", "medium", "high"]


class Tip(BaseModel):
    claim: str
    detail: str
    evidence: Evidence
    effort: Rating
    impact: Rating


class Section(BaseModel):
    heading: str
    body: str
    tips: list[Tip]
    caution: str | None = None


class Source(BaseModel):
    label: str
    note: str


class Guide(BaseModel):
    topic: str
    title: str
    dek: str
    updated: str
    reading_time_min: int
    bottom_line: list[str]
    sections: list[Section]
    sources: list[Source]


class Issue(BaseModel):
    severity: Literal["blocker", "warning"]
    where: str
    message: str


class Report(BaseModel):
    passed: bool
    issues: list[Issue] = Field(default_factory=list)
