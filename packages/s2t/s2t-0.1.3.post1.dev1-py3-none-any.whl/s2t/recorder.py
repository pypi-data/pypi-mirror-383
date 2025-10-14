from __future__ import annotations

import os
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
        # Control queue is separate from audio frames to avoid control backpressure.
        ctrl_q: queue.Queue[str] = queue.Queue()
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
                    if self.verbose:
                        print("[key] using msvcrt (Windows)", file=sys.stderr)
                    while not stop_evt.is_set():
                        if ms.kbhit():
                            ch = ms.getwch()
                            if ch in ("\r", "\n"):
                                if self.verbose:
                                    print("[key] ENTER", file=sys.stderr)
                                evt_q.put("ENTER")
                                break
                            if ch == " ":
                                now = time.perf_counter()
                                if self.debounce_ms and (now - last_space) < (
                                    self.debounce_ms / 1000.0
                                ):
                                    continue
                                last_space = now
                                if self.verbose:
                                    print("[key] SPACE", file=sys.stderr)
                                evt_q.put("SPACE")
                        time.sleep(0.01)
                else:
                    # Prefer sys.stdin when it's a TTY (original, proven path). If not a TTY, try /dev/tty, else fallback to stdin line reads.
                    try:
                        if sys.stdin.isatty():
                            fd = sys.stdin.fileno()
                            if self.verbose:
                                print("[key] using sys.stdin (isatty, fd read)", file=sys.stderr)
                            old = termios.tcgetattr(fd)
                            tty.setcbreak(fd)
                            last_space = 0.0
                            try:
                                while not stop_evt.is_set():
                                    r, _, _ = select.select([fd], [], [], 0.05)
                                    if r:
                                        try:
                                            ch_b = os.read(fd, 1)
                                        except BlockingIOError:
                                            continue
                                        if not ch_b:
                                            continue
                                        ch = ch_b.decode(errors="ignore")
                                        if ch in ("\n", "\r"):
                                            if self.verbose:
                                                print("[key] ENTER", file=sys.stderr)
                                            evt_q.put("ENTER")
                                            break
                                        if ch == " ":
                                            now = time.perf_counter()
                                            if self.debounce_ms and (now - last_space) < (
                                                self.debounce_ms / 1000.0
                                            ):
                                                continue
                                            last_space = now
                                            if self.verbose:
                                                print("[key] SPACE", file=sys.stderr)
                                            evt_q.put("SPACE")
                            finally:
                                termios.tcsetattr(fd, termios.TCSADRAIN, old)
                        else:
                            # Try /dev/tty when stdin is not a TTY
                            using_devtty = False
                            fd = None
                            try:
                                fd = os.open("/dev/tty", os.O_RDONLY)
                                using_devtty = True
                                if self.verbose:
                                    print("[key] using /dev/tty (stdin not TTY)", file=sys.stderr)
                                old = termios.tcgetattr(fd)
                                tty.setcbreak(fd)
                                last_space = 0.0
                                try:
                                    while not stop_evt.is_set():
                                        r, _, _ = select.select([fd], [], [], 0.05)
                                        if r:
                                            ch_b = os.read(fd, 1)
                                            if not ch_b:
                                                continue
                                            ch = ch_b.decode(errors="ignore")
                                            if ch in ("\n", "\r"):
                                                if self.verbose:
                                                    print("[key] ENTER", file=sys.stderr)
                                                evt_q.put("ENTER")
                                                break
                                            if ch == " ":
                                                now = time.perf_counter()
                                                if self.debounce_ms and (now - last_space) < (
                                                    self.debounce_ms / 1000.0
                                                ):
                                                    continue
                                                last_space = now
                                                if self.verbose:
                                                    print("[key] SPACE", file=sys.stderr)
                                                evt_q.put("SPACE")
                                finally:
                                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
                            except Exception:
                                if using_devtty and fd is not None:
                                    try:
                                        os.close(fd)
                                    except Exception:
                                        pass
                                print(
                                    "Warning: no TTY for key input; falling back to stdin line mode.",
                                    file=sys.stderr,
                                )
                                # Last resort: line-buffered stdin; Enter will still end.
                                while not stop_evt.is_set():
                                    line = sys.stdin.readline()
                                    if not line:
                                        time.sleep(0.05)
                                        continue
                                    # If user hits Enter on empty line, treat as ENTER
                                    if line == "\n" or line == "\r\n":
                                        if self.verbose:
                                            print("[key] ENTER (line mode)", file=sys.stderr)
                                        evt_q.put("ENTER")
                                        break
                                    # If first non-empty char is space, treat as SPACE
                                    if line and line[0] == " ":
                                        if self.verbose:
                                            print("[key] SPACE (line mode)", file=sys.stderr)
                                        evt_q.put("SPACE")
                    except Exception as e:
                        print(f"Warning: key reader failed: {e}", file=sys.stderr)

            except Exception as e:
                # Log unexpected key reader errors to aid debugging, but keep recording running.
                print(f"Warning: key reader stopped unexpectedly: {e}", file=sys.stderr)

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
                # First, handle any pending control commands so SPACE/ENTER are never blocked by frames backlog.
                try:
                    while True:
                        cmd = ctrl_q.get_nowait()
                        if cmd == "split":
                            fh.flush()
                            fh.close()
                            if frames_written > 0:
                                dur = frames_written / float(self.samplerate)
                                chunk_paths.append(cur_path)
                                chunk_frames.append(frames_written)
                                chunk_offsets.append(offset_seconds_total)
                                offset_seconds_total += dur
                                if self.verbose:
                                    print(
                                        f"Saved chunk: {cur_path.name} ({dur:.2f}s)",
                                        file=sys.stderr,
                                    )
                                tx_queue.put(
                                    (chunk_index, cur_path, frames_written, chunk_offsets[-1])
                                )
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
                                str(cur_path),
                                mode="w",
                                samplerate=self.samplerate,
                                channels=self.channels,
                            )
                        elif cmd == "finish":
                            fh.flush()
                            fh.close()
                            if frames_written > 0:
                                dur = frames_written / float(self.samplerate)
                                chunk_paths.append(cur_path)
                                chunk_frames.append(frames_written)
                                chunk_offsets.append(offset_seconds_total)
                                offset_seconds_total += dur
                                if self.verbose:
                                    print(
                                        f"Saved chunk: {cur_path.name} ({dur:.2f}s)",
                                        file=sys.stderr,
                                    )
                                tx_queue.put(
                                    (chunk_index, cur_path, frames_written, chunk_offsets[-1])
                                )
                            else:
                                try:
                                    cur_path.unlink(missing_ok=True)
                                except Exception:
                                    pass
                            tx_queue.put((-1, Path(), 0, 0.0))
                            return
                except queue.Empty:
                    pass

                # Then, write frames if available; short timeout to re-check control queue regularly.
                try:
                    kind, payload = audio_q.get(timeout=0.05)
                except queue.Empty:
                    continue
                if kind == "frames":
                    data = payload
                    fh.write(data)
                    frames_written += len(data)
            tx_queue.put((-1, Path(), 0, 0.0))

        # Timestamp of last dropped-frame warning (throttling for verbose mode)
        last_drop_log = 0.0

        def cb(indata: Any, frames: int, time_info: Any, status: Any) -> None:
            nonlocal last_drop_log
            if status:
                print(status, file=sys.stderr)
            if not self._paused:
                try:
                    audio_q.put_nowait(("frames", indata.copy()))
                except queue.Full:
                    # Drop frame if the queue is saturated; throttle warnings.
                    now = time.perf_counter()
                    if self.verbose and (now - last_drop_log) > 1.0:
                        print(
                            "Warning: audio queue full; dropping input frames.",
                            file=sys.stderr,
                        )
                        last_drop_log = now

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
                    ctrl_q.put("split")
                elif evt == "ENTER":
                    ctrl_q.put("finish")
                    break
        writer_t.join()
        return chunk_paths, chunk_frames, chunk_offsets
