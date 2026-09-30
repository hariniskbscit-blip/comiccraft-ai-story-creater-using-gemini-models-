"""AI services: Gemini Flash (outline), Gemini Pro (narration), Diffusers (panel images)."""
import json
import os
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw

PANEL_DIR = Path(__file__).resolve().parent / "static" / "panels"

_client = None
_sd_pipe = None


def _gemini():
    global _client
    if _client is None:
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY missing. Add it to your .env file.")
        _client = genai.Client(api_key=api_key)
    return _client


def generate_outline(idea: str, genre: str, style: str, num_panels: int) -> list[dict]:
    """Gemini Flash -> comic outline as a list of panels."""
    from google.genai import types

    prompt = f"""You are a comic book writer. Create an outline for a {genre} comic.
Story idea: {idea}
Art style: {style}
Return ONLY JSON: a list of exactly {num_panels} objects with keys:
"panel" (number), "scene" (one-sentence description), "caption" (short caption or dialogue),
"image_prompt" (detailed visual prompt for an image generator, no text in image)."""
    resp = _gemini().models.generate_content(
        model=os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash"),
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    panels = json.loads(resp.text)
    return panels[:num_panels]


def generate_story(idea: str, outline: list[dict]) -> str:
    """Gemini Pro -> full story narration."""
    prompt = (
        "Write an engaging full story narration (3-4 short paragraphs) for this comic.\n"
        f"Idea: {idea}\nPanels: {json.dumps(outline)}"
    )
    resp = _gemini().models.generate_content(
        model=os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"), contents=prompt
    )
    return resp.text.strip()


def _placeholder(path: Path, text: str):
    img = Image.new("RGB", (512, 512), (235, 235, 245))
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, 503, 503], outline=(60, 60, 90), width=4)
    d.multiline_text((30, 30), "\n".join(textwrap.wrap(text, 40)), fill=(30, 30, 60))
    img.save(path)


def _load_sd():
    global _sd_pipe
    if _sd_pipe is None:
        import torch
        from diffusers import StableDiffusionPipeline

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        _sd_pipe = StableDiffusionPipeline.from_pretrained(
            os.getenv("SD_MODEL_ID", "stable-diffusion-v1-5/stable-diffusion-v1-5"),
            torch_dtype=dtype,
        ).to(device)
    return _sd_pipe


def generate_panel_images(comic_id: str, outline: list[dict], style: str) -> list[dict]:
    """Diffusers (Stable Diffusion) -> one image per panel. Falls back to placeholders."""
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    use_sd = os.getenv("USE_DIFFUSERS", "false").lower() == "true"
    panels = []
    for i, p in enumerate(outline, start=1):
        path = PANEL_DIR / f"{comic_id}_{i}.png"
        prompt = f"{p.get('image_prompt', p.get('scene', ''))}, {style} comic style"
        if use_sd:
            _load_sd()(prompt, num_inference_steps=25).images[0].save(path)
        else:
            _placeholder(path, p.get("scene", prompt))
        panels.append({**p, "index": i, "image_path": str(path), "image_url": f"/static/panels/{path.name}"})
    return panels
