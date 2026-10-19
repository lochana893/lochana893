"""Prompt helpers: style presets and the "Magic prompt" expander."""

import re

STYLES = {
    "None (as typed)": "",
    "Realistic": "photorealistic real-life footage, natural lighting, true-to-life colors, sharp details",
    "Cinematic": "cinematic film look, shallow depth of field, dramatic lighting, subtle film grain",
    "Anime": "anime style, vibrant colors, clean line art, expressive motion",
    "3D Cartoon": "3D animated cartoon style, soft global illumination, colorful, Pixar-like",
    "Drone / Travel": "aerial drone shot, sweeping camera movement, golden hour light, epic landscape",
    "Product Ad": "commercial product shot, studio lighting, clean background, slow orbiting camera",
}

QUALITY_TAIL = (
    "High quality, highly detailed, sharp focus, smooth natural motion, "
    "stable camera, consistent subject from start to end."
)

# Short prompts give flat, jittery videos. These hints are only added when the
# user did not already describe the camera or the light.
CAMERA_HINT = "The camera moves slowly and smoothly to follow the action."
LIGHT_HINT = "The scene is well lit with soft, natural light."

_CAMERA_WORDS = re.compile(r"\b(camera|shot|pan|zoom|dolly|tracking|drone|close-up|closeup|angle)\b", re.I)
_LIGHT_WORDS = re.compile(r"\b(light|lighting|lit|sunset|sunrise|night|neon|shadow|golden hour)\b", re.I)


def has_non_latin(text: str) -> bool:
    """True when the prompt contains Sinhala, Tamil or other non-Latin letters."""
    return any(ord(ch) > 0x24F and ch.isalpha() for ch in text)


def build_prompt(user_prompt: str, style: str, magic: bool) -> str:
    prompt = " ".join(user_prompt.split()).strip()
    if not prompt:
        return prompt
    parts = [prompt.rstrip(".") + "."]
    style_text = STYLES.get(style, "")
    if style_text:
        parts.append(style_text[0].upper() + style_text[1:] + ".")
    if magic:
        if not _CAMERA_WORDS.search(prompt):
            parts.append(CAMERA_HINT)
        if not _LIGHT_WORDS.search(prompt) and not style_text:
            parts.append(LIGHT_HINT)
        parts.append(QUALITY_TAIL)
    return " ".join(parts)
