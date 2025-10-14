from __future__ import annotations

import time
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Any

from .types import SegmentDict, TranscriptionResult


class WhisperEngine:
    def __init__(
        self,
        model_name: str,
        translate: bool,
        language: str | None,
        native_segmentation: bool,
        session_dir: Path,
        samplerate: int,
        channels: int,
        verbose: bool = False,
        profile: dict | None = None,
    ) -> None:
        self.model_name = model_name
        self.translate = translate
        self.language = language
        self.native_segmentation = native_segmentation
        self.session_dir = session_dir
        self.samplerate = samplerate
        self.channels = channels
        self.verbose = verbose
        self.profile = profile or {}
        self._executor: ThreadPoolExecutor | None = None

    def preload(self) -> tuple[ThreadPoolExecutor | None, Future | None]:
        try:
            self._executor = ThreadPoolExecutor(max_workers=1)

            def _load(name: str):
                import whisper

                t0 = time.perf_counter()
                m = whisper.load_model(name)
                t1 = time.perf_counter()
                return m, (t1 - t0)

            fut = self._executor.submit(_load, self.model_name)
            return self._executor, fut
        except Exception:
            return None, None

    def resolve_model(self, fut: Future | None):
        import whisper

        model = None
        if fut is not None:
            try:
                model, load_dur = fut.result()
                self.profile["model_load_sec"] = self.profile.get("model_load_sec", 0.0) + float(
                    load_dur
                )
            except Exception:
                model = None
        if model is None:
            t0m = time.perf_counter()
            model = whisper.load_model(self.model_name)
            t1m = time.perf_counter()
            self.profile["model_load_sec"] = self.profile.get("model_load_sec", 0.0) + (t1m - t0m)
        return model

    def transcribe_chunk(
        self,
        model,
        audio_path: Path,
        frames: int,
        initial_prompt: str | None = None,
    ) -> TranscriptionResult:
        task = "translate" if self.translate else "transcribe"
        t0 = time.perf_counter()
        res: dict[str, Any] = model.transcribe(
            str(audio_path),
            task=task,
            language=self.language,
            fp16=False,
            initial_prompt=initial_prompt,
        )
        t1 = time.perf_counter()
        self.profile["transcribe_sec"] = self.profile.get("transcribe_sec", 0.0) + (t1 - t0)
        text_c = str(res.get("text", "") or "").strip()
        if self.native_segmentation:
            segs_raw = res.get("segments", []) or []
            segs_typed: list[SegmentDict] = []
            for s in segs_raw:
                try:
                    start = float(s.get("start", 0.0))
                    end = float(s.get("end", 0.0))
                    text = str(s.get("text", "") or "")
                    segs_typed.append({"start": start, "end": end, "text": text})
                except Exception:
                    continue
            return {"text": text_c, "segments": segs_typed}
        # Collapsed single segment per chunk
        segs_raw = res.get("segments", []) or []
        start = float(segs_raw[0].get("start", 0.0)) if segs_raw else 0.0
        end = float(segs_raw[-1].get("end", 0.0)) if segs_raw else (frames / float(self.samplerate))
        return {
            "text": text_c,
            "segments": ([{"start": start, "end": end, "text": text_c}] if text_c else []),
        }

    def write_chunk_outputs(self, result: TranscriptionResult, audio_path: Path) -> None:
        try:
            from whisper.utils import get_writer

            for fmt in ("txt", "srt", "vtt", "tsv", "json"):
                writer = get_writer(fmt, str(self.session_dir))
                writer(result, str(audio_path))
        except Exception as e:
            if self.verbose:
                print(f"Warning: failed to write chunk outputs for {audio_path.name}: {e}")

    def merge_results(
        self, results: list[TranscriptionResult], offsets: list[float], cumulative_text: str
    ) -> TranscriptionResult:
        merged: TranscriptionResult = {"text": "", "segments": []}
        for res, off in zip(results, offsets, strict=False):
            merged["text"] += res.get("text") or ""
            for s in res.get("segments", []):
                s2: SegmentDict = {}
                if "start" in s:
                    s2["start"] = float(s["start"]) + off
                if "end" in s:
                    s2["end"] = float(s["end"]) + off
                if "text" in s:
                    s2["text"] = s["text"]
                merged["segments"].append(s2)
        if (cumulative_text or "").strip():
            merged["text"] = cumulative_text
        return merged
