"""
AIVOX FastAPI Backend — Stateless, Serverless-compatible
Handles: Question generation, Audio transcription, Answer evaluation, Report generation
All heavy AI calls are server-side to keep API keys secure.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

load_dotenv()

from api.routers import interview, report


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: validate required env vars
    required = ["GEMINI_API_KEY", "GROQ_API_KEY"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {missing}")
    yield
    # Shutdown: nothing to clean up (stateless)


app = FastAPI(
    title="AIVOX API",
    description="AI Interview Coach — stateless serverless API",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend origins
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(interview.router, prefix="/api")
app.include_router(report.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
