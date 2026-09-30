# ComicCraft - AI Comic Story Creator (Gemini)

Flow: Browser -> FastAPI (app/main.py) -> Jinja2 templates -> routes.py
(Gemini Flash outline + Gemini Pro story + Stable Diffusion panels)
-> layout_builder.py -> exporters.py (PDF via FPDF) -> comic_preview.html -> export_success.html

## Run
    python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env        # add your GEMINI_API_KEY
    uvicorn app.main:app --reload
Open http://127.0.0.1:8000

## Real Stable Diffusion images
Install diffusers, transformers, accelerate, torch, then set USE_DIFFUSERS=true in .env.
With USE_DIFFUSERS=false, simple placeholder panels are used (good for quick testing).
