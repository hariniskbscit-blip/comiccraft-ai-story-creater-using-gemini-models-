import uuid
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from app import exporters, services
from app.layout_builder import build_layout

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

# Simple in-memory store (use a DB for production)
COMICS: dict[str, dict] = {}


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"error": None})


@router.post("/generate")
async def generate(
    request: Request,
    idea: str = Form(...),
    genre: str = Form("adventure"),
    style: str = Form("colorful cartoon"),
    num_panels: int = Form(4),
):
    num_panels = max(1, min(num_panels, 12))
    comic_id = uuid.uuid4().hex[:8]
    try:
        outline = services.generate_outline(idea, genre, style, num_panels)   # Gemini Flash
        story = services.generate_story(idea, outline)                        # Gemini Pro
        panels = services.generate_panel_images(comic_id, outline, style)     # Diffusers
    except Exception as e:  # show friendly error on the form
        return templates.TemplateResponse(request, "index.html", {"error": str(e)})

    pages = build_layout(panels)
    COMICS[comic_id] = {"title": idea[:60], "story": story, "pages": pages}
    return templates.TemplateResponse(
        request, "comic_preview.html", {"comic_id": comic_id, **COMICS[comic_id]}
    )


@router.post("/export/{comic_id}")
async def export(request: Request, comic_id: str):
    comic = COMICS.get(comic_id)
    if not comic:
        raise HTTPException(404, "Comic not found")
    exporters.export_pdf(comic_id, comic["title"], comic["pages"], comic["story"])
    return templates.TemplateResponse(request, "export_success.html", {"comic_id": comic_id})


@router.get("/download/{comic_id}")
async def download(comic_id: str):
    path = exporters.EXPORT_DIR / f"{comic_id}.pdf"
    if not path.exists():
        raise HTTPException(404, "PDF not found")
    return FileResponse(path, media_type="application/pdf", filename=f"comiccraft_{comic_id}.pdf")
