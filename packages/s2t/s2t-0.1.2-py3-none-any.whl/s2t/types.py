from __future__ import annotations

from typing import TypedDict


class SegmentDict(TypedDict, total=False):
    start: float
    end: float
    text: str


class TranscriptionResult(TypedDict):
    text: str
    segments: list[SegmentDict]
