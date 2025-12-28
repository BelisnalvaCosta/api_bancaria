from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from .database import engine, Base
from .routes import router

app = FastAPI(
    title="API Bancária Assíncrona",
    description="Gerenciamento de depósitos e saques com JWT",
    version="1.0.0"
)

# Pasta frontend (resolve caminho absoluto para evitar problemas ao rodar a app de diferentes CWDs)
BASE_DIR = Path(__file__).resolve().parent.parent / "frontend"

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# APIs ficam em /api; arquivos estáticos e index são servidos pelo FastAPI
app.include_router(router, prefix="/api")
app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")

@app.get("/")
async def root():
    return FileResponse(str(BASE_DIR / "index.html"))