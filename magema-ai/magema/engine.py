"""Loads the open-source video models and turns a prompt (+ optional photo) into an MP4."""

import random
import time
from dataclasses import dataclass
from typing import Callable

from PIL import Image

from .config import MODELS, ModelSpec, fit_size, plan_clips, total_frames
from .video import VideoWriter, fit_image, to_pil

# progress(fraction_done, message)
ProgressFn = Callable[[float, str], None]


@dataclass
class GenerationResult:
    path: str
    seconds: float
    frames: int
    width: int
    height: int
    clips: int
    elapsed: float
    seed: int
    memory_mode: str


def choose_memory_mode(vram_gb: float, spec: ModelSpec) -> str:
    """"gpu" keeps everything on the card, "offload" swaps parts to RAM, "8bit" shrinks weights for 16GB cards."""
    if vram_gb >= spec.full_gpu_gb:
        return "gpu"
    if vram_gb >= 20:
        return "offload"
    return "8bit"


class MagemaEngine:
    def __init__(self, model_key: str = "fast"):
        self.spec = MODELS[model_key]
        self.memory_mode = ""
        self._t2v = None
        self._i2v = None
        self._offloaded_pipe = None

    # ---- loading -------------------------------------------------------

    def load(self) -> None:
        if self._t2v is not None:
            return
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError(
                "GPU එකක් හම්බුනේ නැහැ (no CUDA GPU found). "
                "Colab: Runtime → Change runtime type → T4 GPU තෝරලා නැවත run කරන්න."
            )
        vram_gb = torch.cuda.get_device_properties(0).total_memory / 1024**3
        self.memory_mode = choose_memory_mode(vram_gb, self.spec)
        # Turing cards (T4) have no fast bfloat16, so use float16 there when the model tolerates it.
        fast_bf16 = torch.cuda.get_device_capability(0)[0] >= 8
        dtype = torch.bfloat16 if fast_bf16 or not self.spec.fp16_ok else torch.float16

        kwargs = {"torch_dtype": dtype}
        if self.memory_mode == "8bit":
            from diffusers.quantizers import PipelineQuantizationConfig

            components = ["text_encoder"] + (["transformer"] if self.spec.family == "wan" else [])
            kwargs["quantization_config"] = PipelineQuantizationConfig(
                quant_backend="bitsandbytes_8bit",
                quant_kwargs={"load_in_8bit": True},
                components_to_quantize=components,
            )

        if self.spec.family == "ltx":
            from diffusers import LTXConditionPipeline

            pipe = LTXConditionPipeline.from_pretrained(self.spec.repo, **kwargs)
            t2v = i2v = pipe
        else:
            from diffusers import AutoencoderKLWan, WanImageToVideoPipeline, WanPipeline

            vae = AutoencoderKLWan.from_pretrained(self.spec.repo, subfolder="vae", torch_dtype=torch.float32)
            t2v = WanPipeline.from_pretrained(self.spec.repo, vae=vae, **kwargs)
            i2v = WanImageToVideoPipeline.from_pipe(t2v)

        # Decoding long, high-res clips in tiles keeps VAE memory flat.
        t2v.vae.enable_tiling()
        if self.memory_mode != "offload":
            # 8-bit parts are already on the GPU; this moves the rest.
            t2v.to("cuda")
        self._t2v, self._i2v = t2v, i2v

    def _pipe(self, with_image: bool):
        pipe = self._i2v if with_image else self._t2v
        # Text and image pipelines share weights, so move the offload hooks to whichever runs now.
        if self.memory_mode == "offload" and self._offloaded_pipe is not pipe:
            pipe.enable_model_cpu_offload()
            self._offloaded_pipe = pipe
        return pipe

    # ---- generation ----------------------------------------------------

    def _run_clip(self, *, prompt, negative_prompt, width, height, num_frames, steps, guidance, seed,
                  image=None, video=None, on_step=None):
        """One model call. Returns (F, H, W, 3) float frames in [0, 1]."""
        import torch

        spec = self.spec
        generator = torch.Generator("cpu").manual_seed(seed)

        def callback(pipe, step, timestep, callback_kwargs):
            if on_step:
                on_step(step + 1)
            return callback_kwargs

        common = dict(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_frames=num_frames,
            num_inference_steps=steps,
            guidance_scale=guidance,
            generator=generator,
            output_type="np",
            callback_on_step_end=callback,
        )
        if spec.family == "ltx":
            from diffusers.pipelines.ltx.pipeline_ltx_condition import LTXVideoCondition

            conditions = None
            if video is not None:
                conditions = [LTXVideoCondition(video=video, frame_index=0)]
            elif image is not None:
                conditions = [LTXVideoCondition(image=image, frame_index=0)]
            out = self._pipe(True)(
                conditions=conditions,
                frame_rate=spec.fps,
                decode_timestep=0.05,
                decode_noise_scale=0.025,
                **common,
            )
        elif image is not None:
            out = self._pipe(True)(image=image, **common)
        else:
            out = self._pipe(False)(**common)
        return out.frames[0]

    def generate(
        self,
        prompt: str,
        out_path: str,
        image: Image.Image | None = None,
        seconds: float = 5,
        aspect: float = 9 / 16,
        quality: str = "Best",
        negative_prompt: str | None = None,
        steps: int | None = None,
        guidance: float | None = None,
        seed: int | None = None,
        progress: ProgressFn | None = None,
    ) -> GenerationResult:
        spec = self.spec
        start = time.time()
        progress = progress or (lambda frac, msg: None)
        progress(0.0, f"Loading {spec.repo} (first run downloads the model)…")
        self.load()

        if image is not None:
            aspect = image.width / image.height
        area = spec.best_area if quality == "Best" else spec.draft_area
        width, height = fit_size(aspect, area, spec.mod)
        if image is not None:
            image = fit_image(image, width, height)

        steps = steps or spec.steps
        guidance = guidance or spec.guidance
        negative_prompt = negative_prompt or spec.negative_prompt
        seed = random.randint(0, 2**31 - 1) if seed is None or seed < 0 else seed
        clips = plan_clips(seconds, spec)
        total_steps = steps * len(clips)

        tail = None  # last overlap_frames of the previous clip, as PIL images
        with VideoWriter(out_path, width, height, spec.fps) as writer:
            for i, num_frames in enumerate(clips):
                done = i * steps

                def on_step(step, done=done, i=i):
                    progress((done + step) / total_steps, f"Clip {i + 1}/{len(clips)} • step {step}/{steps}")

                cond_image, cond_video = image, None
                if tail is not None:
                    # LTX continues from several frames (keeps motion); Wan from the last frame.
                    cond_image, cond_video = (None, tail) if spec.family == "ltx" else (tail[-1], None)
                frames = self._run_clip(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    num_frames=num_frames,
                    steps=steps,
                    guidance=guidance,
                    seed=seed + i,
                    image=cond_image,
                    video=cond_video,
                    on_step=on_step,
                )
                # The first overlap_frames of an extension repeat the previous clip's ending.
                writer.write(frames if tail is None else frames[spec.overlap_frames:])
                tail = to_pil(frames[-spec.overlap_frames:])

        frames_out = total_frames(clips, spec)
        return GenerationResult(
            path=out_path,
            seconds=frames_out / spec.fps,
            frames=frames_out,
            width=width,
            height=height,
            clips=len(clips),
            elapsed=time.time() - start,
            seed=seed,
            memory_mode=self.memory_mode,
        )
