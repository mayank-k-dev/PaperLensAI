"""
PaperLensAI – FastAPI Application Entry Point
Medical Literature Summarization Tool powered by Google Gemini
"""
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from routers import summarize, pubmed, batch
from models.schemas import HealthResponse
from services.gemini_service import gemini_service
from services.pubmed_service import pubmed_service

# ── Setup ─────────────────────────────────────────────────────────────────────
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger("paperlensai")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="PaperLensAI",
    description="AI-powered Medical Literature Summarization Tool | TCS Technology Day 2026",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(summarize.router)
app.include_router(pubmed.router)
app.include_router(batch.router)

# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/api/health", response_model=HealthResponse, tags=["system"])
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        gemini_connected=gemini_service.is_connected,
        pubmed_connected=pubmed_service.is_connected,
    )

# ── Serve Frontend UI Directly ───────────────────────────────────────────────
from fastapi.staticfiles import StaticFiles
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")



# ── Startup ───────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    logger.info("🔬 PaperLensAI starting up...")
    logger.info(f"   Gemini connected: {gemini_service.is_connected}")
    logger.info(f"   PubMed connected: {pubmed_service.is_connected}")
    logger.info("🚀 PaperLensAI is ready!")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
