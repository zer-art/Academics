"""AIVOX API — Report Router
Endpoints:
  POST /api/finish  → Generate comprehensive report + save to Firestore
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from api.services.gemini_service import GeminiService

router = APIRouter()
gemini = GeminiService()


# ─── Pydantic Models ──────────────────────────────────────────────────────────
class AnswerScore(BaseModel):
    question: str
    answer: str
    score: int
    feedback: str
    strengths: list[str]
    improvements: list[str]


class ConfidenceSummary(BaseModel):
    average_confidence: float
    peak_confidence: float
    trend: str  # "improving" | "stable" | "declining"
    total_frames: int
    distribution: dict  # {excellent, good, fair, poor}


class FinishRequest(BaseModel):
    role: str
    duration_seconds: int
    answer_scores: list[AnswerScore]
    confidence_summary: ConfidenceSummary
    user_id: Optional[str] = None  # Firebase UID — if provided, save to Firestore


class FinishResponse(BaseModel):
    report: dict
    saved_to_db: bool
    report_id: Optional[str] = None


# ─── Helpers ─────────────────────────────────────────────────────────────────
def _calculate_final_score(answer_scores: list[AnswerScore], confidence: ConfidenceSummary) -> dict:
    """Weighted score: 80% answers, 20% confidence."""
    if not answer_scores:
        return {"final_score": 0, "answer_score": 0, "confidence_score": 0}

    avg_answer = sum(s.score for s in answer_scores) / len(answer_scores)

    # Confidence scoring
    conf_base = confidence.average_confidence
    trend_bonus = {"improving": 5, "declining": -5, "stable": 0}.get(confidence.trend, 0)
    conf_score = min(max(conf_base + trend_bonus, 0), 100)

    final = round((avg_answer * 0.8) + (conf_score * 0.2), 1)

    return {
        "final_score": final,
        "answer_score": round(avg_answer, 1),
        "confidence_score": round(conf_score, 1),
        "breakdown": {"answers": "80%", "confidence": "20%"},
    }


def _format_duration(seconds: int) -> str:
    mins, secs = divmod(seconds, 60)
    return f"{mins}m {secs}s"


# ─── Endpoint ─────────────────────────────────────────────────────────────────
@router.post("/finish", response_model=FinishResponse)
async def finish_interview(request: FinishRequest):
    """
    Generate the comprehensive final report.
    Optionally save to Firestore if user_id is provided.
    """
    try:
        scoring = _calculate_final_score(request.answer_scores, request.confidence_summary)

        # Build the report object
        report = {
            "interview_summary": {
                "role": request.role,
                "duration": _format_duration(request.duration_seconds),
                "questions_answered": len(request.answer_scores),
                "date": None,  # Set client-side (avoids timezone issues)
            },
            "scoring": scoring,
            "question_analysis": [
                {
                    "question": s.question,
                    "answer": s.answer,
                    "score": s.score,
                    "feedback": s.feedback,
                    "strengths": s.strengths,
                    "improvements": s.improvements,
                }
                for s in request.answer_scores
            ],
            "confidence_analysis": request.confidence_summary.model_dump(),
            "recommendations": _build_recommendations(scoring, request.confidence_summary),
        }

        # Save to Firestore if authenticated user
        saved = False
        report_id = None
        if request.user_id:
            try:
                from api.services.firestore_service import FirestoreService
                fs = FirestoreService()
                report_id = await fs.save_report(request.user_id, report)
                saved = True
            except Exception as db_err:
                # Non-fatal — report still returns even if DB write fails
                print(f"[WARN] Firestore save failed: {db_err}")

        return FinishResponse(report=report, saved_to_db=saved, report_id=report_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {e}")


def _build_recommendations(scoring: dict, confidence: ConfidenceSummary) -> list[str]:
    recs = []
    final = scoring["final_score"]
    ans = scoring["answer_score"]
    conf = scoring["confidence_score"]

    if final >= 85:
        recs.append("🏆 Outstanding performance! You're well-prepared for real interviews.")
    elif final >= 70:
        recs.append("💪 Strong performance — a few targeted improvements will make you stand out.")
    elif final >= 55:
        recs.append("📈 Good foundation — focus on deepening your answers with specific examples.")
    else:
        recs.append("🎯 Keep practicing! Consistency is key — try 2-3 mock interviews per week.")

    if ans < 70:
        recs.append("📚 Use the STAR method (Situation, Task, Action, Result) to structure your answers.")
    if conf < 60:
        recs.append("😊 Practice maintaining eye contact and steady posture — it significantly boosts perceived confidence.")
    if confidence.trend == "declining":
        recs.append("⏱️ Focus on staying composed in the second half of interviews — energy management matters.")
    if confidence.trend == "improving":
        recs.append("🚀 Great job warming up! Try to bring that energy from the start of your next interview.")

    return recs
