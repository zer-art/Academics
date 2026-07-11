"""AIVOX API — Interview Router
Endpoints:
  POST /api/questions   → Generate 5 interview questions for a given role
  POST /api/transcribe  → Transcribe audio blob via Groq Whisper
  POST /api/evaluate    → Score + feedback for a single answer via Gemini
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Literal
from api.services.gemini_service import GeminiService
from api.services.groq_service import GroqService

router = APIRouter()
gemini = GeminiService()
groq_svc = GroqService()

# ─── Supported interview domains ─────────────────────────────────────────────
VALID_DOMAINS = {
    "Software Engineer",
    "Data Scientist",
    "Product Manager",
    "UI/UX Designer",
    "DevOps Engineer",
}


# ─── Pydantic Models ──────────────────────────────────────────────────────────
class QuestionsRequest(BaseModel):
    role: str


class QuestionsResponse(BaseModel):
    role: str
    questions: list[str]


class EvaluateRequest(BaseModel):
    question: str
    answer: str
    role: str


class EvaluateResponse(BaseModel):
    score: int
    feedback: str
    strengths: list[str]
    improvements: list[str]


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/questions", response_model=QuestionsResponse)
async def generate_questions(request: QuestionsRequest):
    """Generate 5 domain-specific interview questions using Gemini."""
    role = request.role.strip()
    if role not in VALID_DOMAINS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {sorted(VALID_DOMAINS)}",
        )
    try:
        questions = await gemini.generate_questions(role)
        return QuestionsResponse(role=role, questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {e}")


@router.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe uploaded audio blob using Groq Whisper.
    
    Accepts: audio/webm, audio/wav, audio/ogg, audio/mp4
    Returns: { transcript: str, duration_seconds: float }
    """
    content_type = audio.content_type or "audio/webm"
    base_type = content_type.split(";")[0].strip().lower()
    
    allowed_types = {
        "audio/webm", "audio/wav", "audio/ogg", "audio/mp4", "audio/mpeg",
        "application/octet-stream"  # safe fallback
    }
    if base_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported audio type: {audio.content_type}",
        )

    try:
        audio_bytes = await audio.read()
        if len(audio_bytes) < 1000:  # sanity check — less than 1KB is likely silence
            return {"transcript": "", "duration_seconds": 0.0}

        # Pass clean base type to Groq Service
        result = await groq_svc.transcribe(audio_bytes, base_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_answer(request: EvaluateRequest):
    """Score and provide feedback on a single interview answer using Gemini."""
    if not request.answer.strip():
        return EvaluateResponse(
            score=0,
            feedback="No answer was provided for this question.",
            strengths=[],
            improvements=["Please provide a verbal answer to the question."],
        )
    try:
        result = await gemini.evaluate_answer(
            question=request.question,
            answer=request.answer,
            role=request.role,
        )
        return EvaluateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")
