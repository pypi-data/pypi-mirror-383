from __future__ import annotations

import queue
import select
import sys
import threading
import time
from pathlib import Path
from typing import Any, Protocol, cast, runtime_checkable


class Recorder:
    def __init__(
        self,
        session_dir: Path,
        samplerate: int,
        channels: int,
        ext: str,
        debounce_ms: int = 0,
        verbose: bool = False,
        pause_after_first_chunk: bool = False,
        resume_event: threading.Event | None = None,
    ) -> None:
        self.session_dir = session_dir
        self.samplerate = samplerate
        self.channels = channels
        self.ext = ext
        self.debounce_ms = max(0, int(debounce_ms))
        self.verbose = verbose
        self.pause_after_first_chunk = pause_after_first_chunk
        self.resume_event = resume_event
        self._paused = False

    def run(
        self,
        tx_queue: queue.Queue[tuple[int, Path, int, float]],
    ) -> tuple[list[Path], list[int], list[float]]:
        import platform
        import termios
        import tty

        try:
            import sounddevice as sd
            import soundfile as sf
        except Exception as e:
            raise RuntimeError("sounddevice/soundfile required for recording.") from e

        evt_q: queue.Queue[str] = queue.Queue()
        stop_evt = threading.Event()

        def key_reader() -> None:
            try:
                if platform.system() == "Windows":
                    import msvcrt

                    @runtime_checkable
                    class _MSVCRT(Protocol):
                        def kbhit(self) -> int: ...
                        def getwch(self) -> str: ...

                    ms = cast(_MSVCRT, msvcrt)

                    last_space = 0.0
                    while not stop_evt.is_set():
                        if ms.kbhit():
                            ch = ms.getwch()
                            if ch in ("\r", "\n"):
                                evt_q.put("ENTER")
                                break
                            if ch == " ":
                                now = time.perf_counter()
                                if self.debounce_ms and (now - last_space) < (
                                    self.debounce_ms / 1000.0
                                ):
                                    continue
                                last_space = now
                                evt_q.put("SPACE")
                        time.sleep(0.01)
                else:
                    fd = sys.stdin.fileno()
                    old = termios.tcgetattr(fd)
                    tty.setcbreak(fd)
                    last_space = 0.0
                    try:
                        while not stop_evt.is_set():
                            r, _, _ = select.select([sys.stdin], [], [], 0.05)
                            if r:
                                ch = sys.stdin.read(1)
                                if ch in ("\n", "\r"):
                                    evt_q.put("ENTER")
                                    break
                                if ch == " ":
                                    now = time.perf_counter()
                                    if self.debounce_ms and (now - last_space) < (
                                        self.debounce_ms / 1000.0
                                    ):
                                        continue
                                    last_space = now
                                    evt_q.put("SPACE")
                    finally:
                        termios.tcsetattr(fd, termios.TCSADRAIN, old)
            except Exception:
                pass

        audio_q: queue.Queue[tuple[str, Any]] = queue.Queue(maxsize=128)
        chunk_index = 1
        chunk_paths: list[Path] = []
        chunk_frames: list[int] = []
        chunk_offsets: list[float] = []
        offset_seconds_total = 0.0

        def writer_fn() -> None:
            nonlocal chunk_index, offset_seconds_total
            frames_written = 0
            cur_path = self.session_dir / f"chunk_{chunk_index:04d}{self.ext}"
            fh = sf.SoundFile(
                str(cur_path), mode="w", samplerate=self.samplerate, channels=self.channels
            )
            while True:
                kind, payload = audio_q.get()
                if kind == "frames":
                    data = payload
                    fh.write(data)
                    frames_written += len(data)
                elif kind == "split":
                    fh.flush()
                    fh.close()
                    if frames_written > 0:
                        dur = frames_written / float(self.samplerate)
                        chunk_paths.append(cur_path)
                        chunk_frames.append(frames_written)
                        chunk_offsets.append(offset_seconds_total)
                        offset_seconds_total += dur
                        if self.verbose:
                            print(f"Saved chunk: {cur_path.name} ({dur:.2f}s)", file=sys.stderr)
                        tx_queue.put((chunk_index, cur_path, frames_written, chunk_offsets[-1]))
                    else:
                        try:
                            cur_path.unlink(missing_ok=True)
                        except Exception:
                            pass
                    frames_written = 0
                    chunk_index += 1
                    if (
                        self.pause_after_first_chunk
                        and chunk_index == 2
                        and self.resume_event is not None
                    ):
                        self._paused = True
                        self.resume_event.wait()
                        self._paused = False
                    cur_path = self.session_dir / f"chunk_{chunk_index:04d}{self.ext}"
                    fh = sf.SoundFile(
                        str(cur_path), mode="w", samplerate=self.samplerate, channels=self.channels
                    )
                elif kind == "finish":
                    fh.flush()
                    fh.close()
                    if frames_written > 0:
                        dur = frames_written / float(self.samplerate)
                        chunk_paths.append(cur_path)
                        chunk_frames.append(frames_written)
                        chunk_offsets.append(offset_seconds_total)
                        offset_seconds_total += dur
                        if self.verbose:
                            print(f"Saved chunk: {cur_path.name} ({dur:.2f}s)", file=sys.stderr)
                        tx_queue.put((chunk_index, cur_path, frames_written, chunk_offsets[-1]))
                    else:
                        try:
                            cur_path.unlink(missing_ok=True)
                        except Exception:
                            pass
                    break
            tx_queue.put((-1, Path(), 0, 0.0))

        def cb(indata: Any, frames: int, time_info: Any, status: Any) -> None:
            if status:
                print(status, file=sys.stderr)
            if not self._paused:
                audio_q.put(("frames", indata.copy()))

        key_t = threading.Thread(target=key_reader, daemon=True)
        writer_t = threading.Thread(target=writer_fn, daemon=True)
        key_t.start()
        writer_t.start()

        print("Recording… Press SPACE to split, Enter to finish.")
        print("—" * 60)
        print("")

        import sounddevice as sd

        with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=cb):
            while True:
                try:
                    evt = evt_q.get(timeout=0.05)
                except queue.Empty:
                    continue
                if evt == "SPACE":
                    audio_q.put(("split", None))
                elif evt == "ENTER":
                    audio_q.put(("finish", None))
                    break
        writer_t.join()
        return chunk_paths, chunk_frames, chunk_offsets
