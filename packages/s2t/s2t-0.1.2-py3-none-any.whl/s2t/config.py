from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SessionOptions:
    outdir: Path | None
    rate: int
    channels: int
    recording_format: str
    model: str
    lang: str | None
    translate: bool
    native_segmentation: bool
    verbose: bool
    edit: bool
    debounce_ms: int
    profile: bool
    keep_chunks: bool
    prompt: bool
