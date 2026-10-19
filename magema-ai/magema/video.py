"""Frame helpers and the ffmpeg writer that saves the original-quality MP4."""

import shutil
import subprocess

import numpy as np
from PIL import Image

from .config import OUTPUT_CRF


def find_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if path:
        return path
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def to_uint8(frames) -> np.ndarray:
    """(F, H, W, 3) uint8 from model output: float frames in [0, 1], uint8 frames or PIL images."""
    if isinstance(frames, list):
        frames = np.stack([np.asarray(f.convert("RGB") if isinstance(f, Image.Image) else f) for f in frames])
    frames = np.asarray(frames)
    if frames.dtype != np.uint8:
        frames = (np.clip(frames, 0.0, 1.0) * 255).round().astype(np.uint8)
    return frames


def to_pil(frames) -> list[Image.Image]:
    return [Image.fromarray(f) for f in to_uint8(frames)]


def fit_image(image: Image.Image, width: int, height: int) -> Image.Image:
    """Center-crop the photo to width:height, then resize, so it is never stretched."""
    image = image.convert("RGB")
    src_w, src_h = image.size
    target = width / height
    if src_w / src_h > target:
        crop_w = round(src_h * target)
        left = (src_w - crop_w) // 2
        image = image.crop((left, 0, left + crop_w, src_h))
    else:
        crop_h = round(src_w / target)
        top = (src_h - crop_h) // 2
        image = image.crop((0, top, src_w, top + crop_h))
    return image.resize((width, height), Image.LANCZOS)


class VideoWriter:
    """Streams raw RGB frames into a single H.264 encode: no watermark, no filters, no re-encoding."""

    def __init__(self, path: str, width: int, height: int, fps: int, crf: int = OUTPUT_CRF):
        self.path = path
        self.size = (width, height)
        self.frames_written = 0
        cmd = [
            find_ffmpeg(), "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps), "-i", "-",
            "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", path,
        ]
        self._proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    def write(self, frames) -> None:
        frames = to_uint8(frames)
        if frames.shape[2:0:-1] != self.size:
            raise ValueError(f"frame size {frames.shape[2]}x{frames.shape[1]} != video size {self.size}")
        self._proc.stdin.write(frames.tobytes())
        self.frames_written += len(frames)

    def close(self) -> None:
        self._proc.stdin.close()
        err = self._proc.stderr.read().decode(errors="replace")
        if self._proc.wait() != 0:
            raise RuntimeError(f"ffmpeg failed: {err.strip()}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.close()
        else:
            self._proc.kill()
            self._proc.wait()
