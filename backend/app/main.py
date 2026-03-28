from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine
from app.models import Base
from app.routers.scan import router as scan_router

STATIC_DIR = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="deaddrop Static Scanner", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# ── Static frontend (production only) ────────────────────────────────────────
# Mount _next assets first so they're served efficiently as static files.
# The catch-all below handles all HTML page routes.
if STATIC_DIR.exists():
    _next_dir = STATIC_DIR / "_next"
    if _next_dir.exists():
        app.mount("/_next", StaticFiles(directory=str(_next_dir)), name="next-assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # trailingSlash: true export → each page is {route}/index.html
        for candidate in [
            STATIC_DIR / full_path / "index.html",
            STATIC_DIR / f"{full_path}.html",
            STATIC_DIR / full_path,          # exact files (favicon.ico etc.)
        ]:
            if candidate.exists() and candidate.is_file():
                return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")
