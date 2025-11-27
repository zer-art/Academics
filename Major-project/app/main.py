from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.src.utils import InterviewController
import base64
import numpy as np
from PIL import Image
from io import BytesIO

app = FastAPI(title="Aivox.io")

# Configure templates
templates = Jinja2Templates(directory="app/templates")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests
class StartInterviewRequest(BaseModel):
    user_role: str


class RecordAnswerRequest(BaseModel):
    session_id: str = "default"


class EmotionAnalysisRequest(BaseModel):
    image: str  # base64 encoded image


class FinishInterviewRequest(BaseModel):
    session_id: str = "default"


# Global interview controller
interview_controller = None

# Serve static assets from landing directory
app.mount("/assets", StaticFiles(directory="landing/assets"), name="assets")


@app.get("/", response_class=FileResponse)
async def index():
    return FileResponse("landing/index.html")


@app.get("/interview")
async def interview_page(request: Request):
    user_role = request.query_params.get("domain", "Software Engineer")
    context = {
        "request": request,
        "title": "AI Interview Coach - Interview Session",
        "user_role": user_role,
    }
    return templates.TemplateResponse("interview.html", context)


@app.get("/report")
async def report_page(request: Request):
    context = {"request": request, "title": "Interview Report - AI Interview Coach"}
    return templates.TemplateResponse("report.html", context)


# Interview System Endpoints
@app.post("/start_interview")
async def start_interview(request: StartInterviewRequest):
    """Start a new interview session"""
    global interview_controller

    try:
        # Initialize interview controller
        interview_controller = InterviewController(request.user_role)

        # Start audio monitoring
        interview_controller.audio_handler.start_listening()

        # Generate initial questions
        questions = interview_controller.session.initialize_questions()

        return JSONResponse(
            content={
                "success": True,
                "questions": questions,
                "message": f"Interview initialized for {request.user_role}",
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start interview: {str(e)}"
        )


@app.get("/ask_question/{question_index}")
async def ask_question(question_index: int):
    """Ask a specific question with echo prevention"""
    global interview_controller

    if not interview_controller or question_index >= len(
        interview_controller.session.questions
    ):
        raise HTTPException(status_code=404, detail="Invalid question index")

    try:
        question = interview_controller.session.questions[question_index]

        # Ask question with state management
        await interview_controller.ask_question(question)

        return JSONResponse(
            content={
                "success": True,
                "question": question,
                "question_index": question_index,
                "state": interview_controller.audio_handler.get_state().value,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ask question: {str(e)}")


@app.post("/record_answer")
async def record_answer(request: RecordAnswerRequest):
    """Wait for user answer with echo prevention"""
    global interview_controller

    if not interview_controller:
        raise HTTPException(status_code=400, detail="Interview not initialized")

    try:
        # Get user answer with state management
        answer = await interview_controller.get_user_answer()

        # Score the answer
        current_question_index = len(interview_controller.session.answers)
        if current_question_index < len(interview_controller.session.questions):
            current_question = interview_controller.session.questions[
                current_question_index
            ]

            # Process in PROCESSING state
            await interview_controller.process_answer(current_question, answer)

            # Get the latest score
            latest_score = interview_controller.answer_scores[-1]

            return JSONResponse(
                content={
                    "success": True,
                    "answer": answer,
                    "score": latest_score["score"],
                    "feedback": latest_score["feedback"],
                    "state": interview_controller.audio_handler.get_state().value,
                }
            )
        else:
            raise HTTPException(status_code=400, detail="No more questions available")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to record answer: {str(e)}"
        )


@app.post("/analyze_confidence")
async def analyze_confidence(request: EmotionAnalysisRequest):
    """Analyze confidence from webcam frame using MediaPipe"""
    global interview_controller

    if not interview_controller:
        raise HTTPException(status_code=400, detail="Interview not initialized")

    try:
        # Remove data URL prefix if present
        image_data = request.image
        if image_data.startswith("data:image"):
            image_data = image_data.split(",")[1]

        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(BytesIO(image_bytes))
        frame = np.array(image)

        # Analyze confidence (not emotion)
        result = interview_controller.add_confidence_data(frame)

        return JSONResponse(content=result)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Confidence analysis failed: {str(e)}"
        )


@app.post("/finish_interview")
async def finish_interview(request: FinishInterviewRequest):
    """Finish interview and generate comprehensive report with confidence analysis"""
    global interview_controller

    if not interview_controller:
        raise HTTPException(status_code=400, detail="Interview not initialized")

    try:
        # Stop audio monitoring
        interview_controller.audio_handler.stop_listening()

        # Generate final report with confidence analysis (not emotion)
        confidence_summary = (
            interview_controller.confidence_analyzer.get_confidence_summary()
        )
        final_report = (
            interview_controller.report_generator.generate_comprehensive_report(
                interview_controller.session,
                interview_controller.answer_scores,
                confidence_summary,
            )
        )

        # Cleanup audio resources
        interview_controller.session.cleanup()

        return JSONResponse(content={"success": True, "report": final_report})

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to finish interview: {str(e)}"
        )


@app.post("/test_audio")
async def test_audio():
    """Test audio system functionality"""
    try:
        from app.src.utils import InterviewSession

        test_session = InterviewSession("Test")

        # Test audio devices
        devices_ok = test_session.test_audio_devices()

        # Cleanup
        test_session.cleanup()

        return JSONResponse(
            content={"success": devices_ok, "message": "Audio test completed"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio test failed: {str(e)}")


@app.get("/interview_state")
async def get_interview_state():
    """Get current interview state for debugging"""
    global interview_controller

    if not interview_controller:
        return JSONResponse(content={"state": "not_initialized"})

    return JSONResponse(
        content={
            "state": interview_controller.audio_handler.get_state().value,
            "is_ai_speaking": interview_controller.audio_handler.is_ai_speaking,
            "is_recording": interview_controller.audio_handler.is_recording,
            "is_listening": interview_controller.audio_handler.is_listening,
        }
    )


@app.get("/health")
async def health_check():
    """Health check for all services"""
    return {
        "status": "healthy",
        "services": {
            "deepface": True,
            "interview_system": True,
            "audio_processing": True,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
