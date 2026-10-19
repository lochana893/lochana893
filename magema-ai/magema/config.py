"""Model specs, size/duration maths and limits for Magema AI."""

import math
from dataclasses import dataclass

# Longest finished video the app will build by chaining clips together.
MAX_TOTAL_SECONDS = 60

# Output encoding: H.264 at CRF 12 is visually lossless and still plays on phones.
OUTPUT_CRF = 12


@dataclass(frozen=True)
class ModelSpec:
    key: str
    label: str
    family: str  # "ltx" or "wan"
    repo: str
    fps: int
    frame_step: int  # num_frames must be frame_step * k + 1
    max_frames: int  # longest single clip the model handles well
    best_area: int  # width * height budget for "Best" quality
    draft_area: int  # width * height budget for "Fast draft"
    mod: int  # width and height must be divisible by this
    steps: int
    guidance: float
    overlap_frames: int  # frames of the previous clip reused when extending
    full_gpu_gb: int  # VRAM needed to keep the whole pipeline on the GPU
    fp16_ok: bool  # False when float16 overflows (black frames); bfloat16 is used even on T4 then
    negative_prompt: str

    @property
    def max_clip_seconds(self) -> float:
        return (self.max_frames - 1) / self.fps


MODELS = {
    "fast": ModelSpec(
        key="fast",
        label="⚡ Fast — LTX-Video 0.9.5 (free Colab T4 OK, 1 clip ≤ 10s)",
        family="ltx",
        repo="Lightricks/LTX-Video-0.9.5",
        fps=24,
        frame_step=8,
        max_frames=257,
        best_area=768 * 512,
        draft_area=512 * 352,
        mod=32,
        steps=40,
        guidance=3.0,
        overlap_frames=17,
        full_gpu_gb=18,
        fp16_ok=False,
        negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted, watermark, text",
    ),
    "hq": ModelSpec(
        key="hq",
        label="💎 HQ — Wan 2.2 TI2V-5B (best quality, 24GB+ GPU, 1 clip ≤ 5s)",
        family="wan",
        repo="Wan-AI/Wan2.2-TI2V-5B-Diffusers",
        fps=24,
        frame_step=4,
        max_frames=121,
        best_area=1280 * 704,
        draft_area=832 * 480,
        mod=32,
        steps=50,
        guidance=5.0,
        overlap_frames=1,
        full_gpu_gb=30,
        fp16_ok=True,
        negative_prompt=(
            "Bright tones, overexposed, static, blurred details, subtitles, style, works, paintings, images, "
            "static, overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, "
            "extra fingers, poorly drawn hands, poorly drawn faces, deformed, disfigured, misshapen limbs, "
            "fused fingers, still picture, messy background, three legs, many people in the background, "
            "walking backwards, watermark, text"
        ),
    ),
}

# Width / height ratio used for text-to-video. A photo's own ratio wins when one is given.
ASPECTS = {
    "9:16 (TikTok / Reels / Shorts)": 9 / 16,
    "16:9 (YouTube)": 16 / 9,
    "1:1 (Instagram)": 1.0,
}

QUALITIES = ("Best", "Fast draft")


def fit_size(aspect: float, max_area: int, mod: int) -> tuple[int, int]:
    """(width, height) close to max_area with the given width/height ratio, both divisible by mod."""
    height = math.sqrt(max_area / aspect)
    width = height * aspect
    return max(mod, round(width / mod) * mod), max(mod, round(height / mod) * mod)


def snap_frames(n: int, spec: ModelSpec) -> int:
    """Smallest valid frame count (frame_step * k + 1) holding at least n frames, capped at max_frames."""
    k = max(1, math.ceil((n - 1) / spec.frame_step))
    return min(spec.max_frames, k * spec.frame_step + 1)


def plan_clips(total_seconds: float, spec: ModelSpec) -> list[int]:
    """Frame count of every clip needed for total_seconds: the first clip plus any extensions.

    Each extension re-generates the last overlap_frames of the previous clip so motion
    carries over, so only (n - overlap_frames) of its frames are new.
    """
    total_seconds = min(max(total_seconds, 1), MAX_TOTAL_SECONDS)
    target = round(total_seconds * spec.fps) + 1
    clips: list[int] = []
    produced = 0
    while produced < target:
        if not clips:
            n = snap_frames(target, spec)
            produced = n
        else:
            n = snap_frames(target - produced + spec.overlap_frames, spec)
            produced += n - spec.overlap_frames
        clips.append(n)
    return clips


def total_frames(clips: list[int], spec: ModelSpec) -> int:
    return clips[0] + sum(n - spec.overlap_frames for n in clips[1:])
