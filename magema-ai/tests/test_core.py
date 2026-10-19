"""CPU-only tests: size/duration maths, prompt builder, ffmpeg writer and clip chaining.

The real models need a CUDA GPU, so the engine test swaps in a fake model call.
Run:  python -m pytest tests
"""

import re
import subprocess

import numpy as np
import pytest
from PIL import Image

from magema.config import MAX_TOTAL_SECONDS, MODELS, fit_size, plan_clips, total_frames
from magema.engine import MagemaEngine, choose_memory_mode
from magema.prompts import CAMERA_HINT, build_prompt, has_non_latin
from magema.video import VideoWriter, find_ffmpeg, fit_image


def count_frames(path: str) -> tuple[int, int, int]:
    """(frames, width, height) of an mp4, decoded with ffmpeg."""
    out = subprocess.run(
        [find_ffmpeg(), "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True,
    )
    for line in out.stderr.decode().splitlines():
        if "Video:" in line:
            w, h = map(int, re.search(r"\b(\d{2,5})x(\d{2,5})\b", line).groups())
            return len(out.stdout) // (w * h * 3), w, h
    raise AssertionError("no video stream")


@pytest.mark.parametrize("key", list(MODELS))
@pytest.mark.parametrize("seconds", [1, 2, 5, 10, 11, 17.5, 30, MAX_TOTAL_SECONDS, 500])
def test_plan_clips_covers_duration_with_valid_clips(key, seconds):
    spec = MODELS[key]
    clips = plan_clips(seconds, spec)
    for n in clips:
        assert (n - 1) % spec.frame_step == 0
        assert spec.frame_step < n <= spec.max_frames
    for n in clips[1:]:
        assert n > spec.overlap_frames
    wanted = min(seconds, MAX_TOTAL_SECONDS) * spec.fps
    produced = total_frames(clips, spec)
    assert produced >= wanted
    # never more than one extra frame_step of overshoot
    assert produced <= wanted + spec.frame_step + 1


def test_single_clip_limits():
    assert plan_clips(10, MODELS["fast"]) == [241]
    assert plan_clips(5, MODELS["hq"]) == [121]
    assert len(plan_clips(60, MODELS["fast"])) > 1


@pytest.mark.parametrize("aspect", [9 / 16, 16 / 9, 1.0, 4 / 3, 3 / 4])
@pytest.mark.parametrize("key", list(MODELS))
def test_fit_size(aspect, key):
    spec = MODELS[key]
    w, h = fit_size(aspect, spec.best_area, spec.mod)
    assert w % spec.mod == 0 and h % spec.mod == 0
    assert w * h <= spec.best_area * 1.1
    assert abs(w / h - aspect) / aspect < 0.1


def test_wan_native_720p():
    assert fit_size(16 / 9, MODELS["hq"].best_area, 32) == (1280, 704)
    assert fit_size(9 / 16, MODELS["hq"].best_area, 32) == (704, 1280)


def test_fit_image_crops_without_stretching():
    img = Image.new("RGB", (1000, 500), "red")
    out = fit_image(img, 320, 320)
    assert out.size == (320, 320)


def test_build_prompt():
    assert build_prompt("   ", "Realistic", True) == ""
    plain = build_prompt("a cat  jumping", "None (as typed)", False)
    assert plain == "a cat jumping."
    magic = build_prompt("a cat jumping", "Cinematic", True)
    assert magic.startswith("a cat jumping.") and "camera" in magic and "High quality" in magic
    # user already described the camera -> no extra camera hint
    own_cam = build_prompt("drone shot of a waterfall", "None (as typed)", True)
    assert CAMERA_HINT not in own_cam


def test_has_non_latin():
    assert has_non_latin("බල්ලෙක් දුවනවා")
    assert not has_non_latin("a dog running, café")


def test_choose_memory_mode():
    assert choose_memory_mode(15, MODELS["fast"]) == "8bit"
    assert choose_memory_mode(24, MODELS["fast"]) == "gpu"
    assert choose_memory_mode(24, MODELS["hq"]) == "offload"
    assert choose_memory_mode(80, MODELS["hq"]) == "gpu"


def test_video_writer_roundtrip(tmp_path):
    path = str(tmp_path / "w.mp4")
    with VideoWriter(path, 64, 32, 24) as w:
        w.write(np.random.rand(5, 32, 64, 3).astype(np.float32))
        w.write([Image.new("RGB", (64, 32), "blue")] * 3)
    assert count_frames(path) == (8, 64, 32)


def test_video_writer_rejects_wrong_size(tmp_path):
    with pytest.raises(ValueError):
        with VideoWriter(str(tmp_path / "bad.mp4"), 64, 32, 24) as w:
            w.write(np.zeros((2, 64, 64, 3), np.uint8))


class FakeEngine(MagemaEngine):
    """Stands in for the GPU model: returns frames whose brightness encodes the frame number."""

    def __init__(self, key):
        super().__init__(key)
        self.calls = []

    def load(self):
        self.memory_mode = "fake"

    def _run_clip(self, *, width, height, num_frames, steps, image=None, video=None, on_step=None, **kw):
        self.calls.append({"frames": num_frames, "image": image, "video": video, "size": (width, height)})
        for s in range(steps):
            on_step(s + 1)
        frames = np.zeros((num_frames, height, width, 3), np.float32)
        frames[..., 0] = np.linspace(0, 1, num_frames)[:, None, None]
        return frames


@pytest.mark.parametrize("key", list(MODELS))
def test_engine_chains_clips_into_one_video(tmp_path, key):
    spec = MODELS[key]
    engine = FakeEngine(key)
    progress = []
    photo = Image.new("RGB", (900, 1600), "green")
    result = engine.generate(
        "test", str(tmp_path / "out.mp4"), image=photo, seconds=12, quality="Fast draft", steps=3,
        progress=lambda f, m: progress.append(f),
    )
    clips = plan_clips(12, spec)
    assert result.clips == len(clips) > 1
    assert [c["frames"] for c in engine.calls] == clips
    # first clip starts from the photo, resized to the video size
    assert engine.calls[0]["image"].size == (result.width, result.height)
    # extensions continue from the previous clip's tail
    for call in engine.calls[1:]:
        if spec.family == "ltx":
            assert call["image"] is None and len(call["video"]) == spec.overlap_frames
        else:
            assert call["video"] is None and call["image"].size == (result.width, result.height)
    assert result.width < result.height  # photo was portrait
    assert count_frames(result.path) == (result.frames, result.width, result.height)
    assert result.frames == total_frames(clips, spec)
    assert progress[-1] == pytest.approx(1.0)
