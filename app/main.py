from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.routes import router  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="ComicCraft - AI Comic Story Creator")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(router)
