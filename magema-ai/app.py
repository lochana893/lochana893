"""Magema AI — free prompt/photo → video web app (Gradio).

Run:  python app.py --share
"""

import argparse
import gc
import os
import time

import gradio as gr

from magema.config import ASPECTS, MAX_TOTAL_SECONDS, MODELS, QUALITIES
from magema.engine import MagemaEngine
from magema.prompts import STYLES, build_prompt, has_non_latin

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

_engine: MagemaEngine | None = None


def get_engine(model_key: str) -> MagemaEngine:
    """Keep one model in memory at a time; switching frees the old one first."""
    global _engine
    if _engine is None or _engine.spec.key != model_key:
        _engine = None
        gc.collect()
        try:
            import torch

            torch.cuda.empty_cache()
        except Exception:
            pass
        _engine = MagemaEngine(model_key)
    return _engine


def generate(prompt, photo, model_key, seconds, aspect_name, quality, style, magic, negative, steps, guidance,
             seed, progress=gr.Progress()):
    if not prompt or not prompt.strip():
        raise gr.Error("Prompt එකක් type කරන්න (please type a prompt).")
    final_prompt = build_prompt(prompt, style, magic)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"magema_{time.strftime('%Y%m%d_%H%M%S')}.mp4")

    engine = get_engine(model_key)
    try:
        result = engine.generate(
            final_prompt,
            out_path,
            image=photo,
            seconds=float(seconds),
            aspect=ASPECTS[aspect_name],
            quality=quality,
            negative_prompt=negative.strip() or None,
            steps=int(steps) or None,
            guidance=float(guidance) or None,
            seed=int(seed),
            progress=lambda frac, msg: progress(frac, desc=msg),
        )
    except Exception as e:
        if "out of memory" in str(e).lower():
            raise gr.Error("GPU memory මදි. 'Fast draft' quality හෝ අඩු තත්පර ගණනක් try කරන්න.") from e
        raise gr.Error(str(e)) from e

    minutes, secs = divmod(int(result.elapsed), 60)
    info = (
        f"✅ **Video එක ready!** {result.seconds:.1f}s • {result.frames} frames • "
        f"{result.width}×{result.height} @ {engine.spec.fps}fps • {result.clips} clip(s) • "
        f"seed `{result.seed}` • {minutes}m {secs}s • GPU mode: {result.memory_mode}\n\n"
        f"**Prompt used:** {final_prompt}"
    )
    if has_non_latin(prompt):
        info += "\n\n⚠️ සිංහල අකුරු model එකට හොඳට තේරෙන්නේ නැහැ — හොඳම result එකට prompt එක English වලින් ලියන්න."
    return result.path, result.path, info


def build_ui() -> gr.Blocks:
    limits = " • ".join(
        f"**{spec.label.split(' (')[0]}**: 1 clip ≤ {spec.max_clip_seconds:.0f}s" for spec in MODELS.values()
    )
    with gr.Blocks(title="Magema AI") as demo:
        gr.Markdown(
            "# 🎬 Magema AI\n"
            "Prompt එකක් දෙන්න (photo එකකුත් දාන්න පුළුවන්) → **original quality** video එකක් ගන්න. "
            "Watermark නැහැ, filters නැහැ, edit කරන්නේ නැහැ — 100% free & open-source.\n\n"
            f"{limits} • Auto-extend එකෙන් **තත්පර {MAX_TOTAL_SECONDS} දක්වා** එක video එකක් හදනවා."
        )
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(
                    label="Prompt (English වලින් ලිව්වොත් හොඳම result)",
                    lines=4,
                    placeholder="A young man playing football on a beach at sunset, slow motion, camera tracking him",
                )
                photo = gr.Image(label="Photo (optional) — photo එක video එකක් කරන්න", type="pil")
                model_key = gr.Radio(
                    [(spec.label, key) for key, spec in MODELS.items()], value="fast", label="Model"
                )
                seconds = gr.Slider(2, MAX_TOTAL_SECONDS, value=5, step=1, label="Video length (තත්පර / seconds)")
                aspect = gr.Radio(list(ASPECTS), value=next(iter(ASPECTS)), label="Size (photo එකක් දැම්මොත් photo size එක)")
                quality = gr.Radio(list(QUALITIES), value=QUALITIES[0], label="Quality")
                style = gr.Dropdown(list(STYLES), value="Realistic", label="Style")
                magic = gr.Checkbox(value=True, label="✨ Magic prompt (prompt එක auto detail කරනවා)")
                with gr.Accordion("Advanced", open=False):
                    negative = gr.Textbox(label="Negative prompt (empty = model default)", lines=2)
                    steps = gr.Slider(0, 80, value=0, step=1, label="Steps (0 = model default)")
                    guidance = gr.Slider(0, 12, value=0, step=0.5, label="Guidance (0 = model default)")
                    seed = gr.Number(value=-1, precision=0, label="Seed (-1 = random)")
                run = gr.Button("🎬 Generate Video", variant="primary")
            with gr.Column():
                video = gr.Video(label="Video", autoplay=True)
                download = gr.File(label="⬇️ Original MP4 download")
                info = gr.Markdown()
        gr.Examples(
            [
                ["A golden retriever puppy running through a flower field, slow motion, camera tracking at ground level"],
                ["A traditional Sri Lankan perahera at night with decorated elephants, fire dancers and drummers"],
                ["Ocean waves crashing on rocks at Mirissa beach during sunset, aerial drone shot"],
                ["A street football player doing a rainbow flick in a small sandy court, crowd cheering"],
            ],
            inputs=[prompt],
        )
        run.click(
            generate,
            [prompt, photo, model_key, seconds, aspect, quality, style, magic, negative, steps, guidance, seed],
            [video, download, info],
        )
    return demo


def main():
    parser = argparse.ArgumentParser(description="Magema AI video generator")
    parser.add_argument("--share", action="store_true", help="create a public gradio.live link (use on Colab)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    build_ui().queue(default_concurrency_limit=1).launch(
        share=args.share,
        server_name=args.host,
        server_port=args.port,
        allowed_paths=[OUTPUT_DIR],
        theme=gr.themes.Soft(),
    )


if __name__ == "__main__":
    main()
