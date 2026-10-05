"""Frame export and MP4 assembly (WI-O1).

Contract
--------
`export_frames(frames, out_dir, fps=30, hold_s=…)` writes zero-padded PNGs at 1920x1080 with a
deterministic frame count; `to_mp4(out_dir, out_path, fps=30)` calls ffmpeg (libx264, yuv420p,
crf 18). Same inputs -> same frame files (byte-identical PNGs).
"""


def export_frames(frames: list, out_dir: str, fps: int = 30, hold_s: float = 1.0) -> list[str]:
    raise NotImplementedError("WI-O1")


def to_mp4(frames_dir: str, out_path: str, fps: int = 30) -> str:
    raise NotImplementedError("WI-O1")
