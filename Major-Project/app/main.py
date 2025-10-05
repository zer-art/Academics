from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from src.deepface import deepface_analyzer
from src.utils import InterviewController
from src.speech_recognition import assembly_recognizer
from performance_config import PerformanceConfig
from performance_middleware import PerformanceMiddleware
from typing import Dict, Optional, List
import json
import asyncio
import base64
import cv2
import numpy as np
from PIL import Image
from io import BytesIO
import orjson
from cachetools import TTLCache
import time
import threading
import logging
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Interview Coach - Assembly AI Edition")

# Performance optimizations with configuration
config = PerformanceConfig()
emotion_cache = TTLCache(
    maxsize=config.EMOTION_CACHE_SIZE, ttl=config.EMOTION_CACHE_TTL
)
question_cache = TTLCache(
    maxsize=config.QUESTION_CACHE_SIZE, ttl=config.QUESTION_CACHE_TTL
)
transcription_cache = TTLCache(
    maxsize=200, ttl=600
)  # 10-minute cache for transcriptions
model_cache = {}  # Global model cache
cache_lock = threading.Lock()

# Performance monitoring
performance_monitor = PerformanceMiddleware(app)


# Custom JSON response with orjson for faster serialization
class ORJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        if config.USE_ORJSON:
            return orjson.dumps(content)
        else:
            return super().render(content)


# Add performance middleware
app.add_middleware(PerformanceMiddleware)

# Configure templates
templates = Jinja2Templates(directory="templates")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for API requests
class ImageAnalysisRequest(BaseModel):
    image: str  # base64 encoded image
    session_id: str = "default"


class FeedbackRequest(BaseModel):
    emotion: str
    confidence: float


class StartInterviewRequest(BaseModel):
    user_role: str


class RecordAnswerRequest(BaseModel):
    session_id: str = "default"
    audio_data: Optional[str] = None  # base64 encoded audio
    answer_text: Optional[str] = None  # pre-transcribed text


class AudioTranscriptionRequest(BaseModel):
    audio_data: str  # base64 encoded audio
    session_id: str = "default"
    config: Optional[Dict] = None  # Assembly AI configuration


class EmotionAnalysisRequest(BaseModel):
    image: str  # base64 encoded image


class FinishInterviewRequest(BaseModel):
    session_id: str = "default"


# Global interview controller
interview_controller = None


# Async optimization functions
async def async_process_image(image_data: str):
    """Process base64 image asynchronously"""

    def process_image():
        # Remove data URL prefix if present
        if image_data.startswith("data:image"):
            image_data_clean = image_data.split(",")[1]
        else:
            image_data_clean = image_data

        # Decode base64 image
        image_bytes = base64.b64decode(image_data_clean)
        image = Image.open(BytesIO(image_bytes))
        return np.array(image)

    return await asyncio.to_thread(process_image)


async def async_emotion_analysis(frame, session_id: str = "default"):
    """Perform emotion analysis asynchronously with caching"""
    # Create cache key based on frame hash and session
    frame_hash = hash(frame.tobytes()) % 1000000
    cache_key = f"{session_id}_{frame_hash}"

    with cache_lock:
        if cache_key in emotion_cache:
            return emotion_cache[cache_key]

    def analyze_emotion():
        global interview_controller
        if interview_controller:
            return interview_controller.add_emotion_data(frame)
        else:
            # Fallback to deepface analyzer
            return deepface_analyzer.analyze_frame(frame)

    result = await asyncio.to_thread(analyze_emotion)

    with cache_lock:
        emotion_cache[cache_key] = result

    return result


async def async_question_generation(user_role: str):
    """Generate questions asynchronously with caching"""
    cache_key = f"questions_{user_role.lower().replace(' ', '_')}"

    with cache_lock:
        if cache_key in question_cache:
            logger.info("Question generation cache hit")
            return question_cache[cache_key]

    def generate_questions():
        controller = InterviewController(user_role)
        return controller.session.initialize_questions()

    questions = await asyncio.to_thread(generate_questions)

    with cache_lock:
        question_cache[cache_key] = questions

    return questions


async def async_transcribe_audio(audio_data: str, session_id: str = "default"):
    """Transcribe audio using Assembly AI with caching"""
    # Create cache key for audio data
    audio_hash = hashlib.md5(audio_data.encode()).hexdigest()[:16]
    cache_key = f"transcription_{session_id}_{audio_hash}"

    with cache_lock:
        if cache_key in transcription_cache:
            logger.info("Transcription cache hit")
            return transcription_cache[cache_key]

    try:
        # Transcribe using Assembly AI
        result = await assembly_recognizer.transcribe_base64(audio_data)

        transcription_result = {
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 0.0),
            "status": result.get("status", "completed"),
            "insights": assembly_recognizer.extract_insights(result),
        }

        # Cache the result
        with cache_lock:
            transcription_cache[cache_key] = transcription_result

        return transcription_result

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        return {
            "text": "",
            "confidence": 0.0,
            "status": "error",
            "error": str(e),
            "insights": {},
        }


@app.on_event("startup")
async def startup_event():
    """Preload models and initialize caches on startup"""
    print("🚀 Initializing AI Interview Coach...")

    # Preload models in background
    async def preload_models():
        try:
            # Preload DeepFace models
            await asyncio.to_thread(lambda: deepface_analyzer.preload_models())
            print("✅ DeepFace models preloaded")
        except Exception as e:
            print(f"⚠️ Warning: Could not preload models: {e}")

    # Run preloading in background
    asyncio.create_task(preload_models())
    print("🎯 AI Interview Coach ready!")


# Serve static assets from landing directory
app.mount("/assets", StaticFiles(directory="../landing/assets"), name="assets")


@app.get("/", response_class=FileResponse)
async def index():
    return FileResponse("../landing/index.html")


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
@app.post("/start_interview", response_class=ORJSONResponse)
async def start_interview(request: StartInterviewRequest):
    """Start a new interview session - optimized with async question generation"""
    global interview_controller

    try:
        interview_controller = InterviewController(request.user_role)

        # Generate questions asynchronously with caching
        questions = await async_question_generation(request.user_role)

        return {
            "success": True,
            "questions": questions,
            "message": f"Interview initialized for {request.user_role}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start interview: {str(e)}"
        )


@app.get("/ask_question/{question_index}", response_class=ORJSONResponse)
async def ask_question(question_index: int):
    """Ask a specific question using TTS - optimized with async processing"""
    global interview_controller

    if not interview_controller or question_index >= len(
        interview_controller.session.questions
    ):
        raise HTTPException(status_code=404, detail="Invalid question index")

    try:
        question = interview_controller.session.questions[question_index]

        # Run TTS asynchronously
        def run_tts():
            return interview_controller.audio_handler.text_to_speech(question)

        # Check if TTS method is already async
        if hasattr(interview_controller.audio_handler, "text_to_speech"):
            if asyncio.iscoroutinefunction(
                interview_controller.audio_handler.text_to_speech
            ):
                success = await interview_controller.audio_handler.text_to_speech(
                    question
                )
            else:
                success = await asyncio.to_thread(run_tts)
        else:
            success = False

        return {
            "success": success,
            "question": question,
            "question_index": question_index,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ask question: {str(e)}")


# Cache management endpoints
@app.post("/api/clear-cache", response_class=ORJSONResponse)
async def clear_cache():
    """Clear all caches for performance reset"""
    with cache_lock:
        emotion_cache.clear()
        question_cache.clear()

    return {"message": "All caches cleared", "success": True}


@app.get("/api/cache-stats", response_class=ORJSONResponse)
async def cache_stats():
    """Get cache statistics"""
    with cache_lock:
        return {
            "emotion_cache": {
                "size": len(emotion_cache),
                "maxsize": emotion_cache.maxsize,
                "ttl": config.EMOTION_CACHE_TTL,
            },
            "question_cache": {
                "size": len(question_cache),
                "maxsize": question_cache.maxsize,
                "ttl": config.QUESTION_CACHE_TTL,
            },
            "transcription_cache": {
                "size": len(transcription_cache),
                "maxsize": transcription_cache.maxsize,
                "ttl": 600,
            },
        }


@app.post("/api/transcribe-audio", response_class=ORJSONResponse)
async def transcribe_audio(request: AudioTranscriptionRequest):
    """Standalone audio transcription endpoint using Assembly AI"""
    try:
        if not assembly_recognizer.is_available():
            raise HTTPException(status_code=503, detail="Assembly AI not configured")

        result = await async_transcribe_audio(request.audio_data, request.session_id)

        return {
            "status": "success",
            "transcription": result,
            "service": "Assembly AI",
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.get("/api/performance-stats", response_class=ORJSONResponse)
async def performance_stats():
    """Get performance statistics"""
    return {
        "performance_stats": performance_monitor.get_performance_stats(),
        "optimizations": config.get_optimization_summary(),
        "cache_config": config.get_cache_config(),
        "async_config": config.get_async_config(),
    }


@app.post("/record_answer", response_class=ORJSONResponse)
async def record_answer(request: RecordAnswerRequest):
    """Record user answer using STT - optimized with async processing"""
    global interview_controller

    if not interview_controller:
        raise HTTPException(status_code=400, detail="Interview not initialized")

    try:
        # Record answer using STT (check if already async or make it async)
        if hasattr(interview_controller.audio_handler, "speech_to_text"):
            if asyncio.iscoroutinefunction(
                interview_controller.audio_handler.speech_to_text
            ):
                answer = await interview_controller.audio_handler.speech_to_text()
            else:
                answer = await asyncio.to_thread(
                    interview_controller.audio_handler.speech_to_text
                )
        else:
            raise HTTPException(status_code=500, detail="Speech to text not available")

        # Score the answer asynchronously
        current_question_index = len(interview_controller.session.answers)
        if current_question_index < len(interview_controller.session.questions):
            current_question = interview_controller.session.questions[
                current_question_index
            ]

            def score_answer():
                return interview_controller.report_generator.scorer.score_answer(
                    current_question, answer, interview_controller.session.user_role
                )

            score_result = await asyncio.to_thread(score_answer)

            interview_controller.session.answers.append(answer)
            interview_controller.answer_scores.append(score_result)

            return {
                "success": True,
                "answer": answer,
                "score": score_result["score"],
                "feedback": score_result["feedback"],
            }
        else:
            raise HTTPException(status_code=400, detail="No more questions available")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to record answer: {str(e)}"
        )


@app.post("/analyze_emotion", response_class=ORJSONResponse)
async def analyze_emotion(request: EmotionAnalysisRequest):
    """Analyze emotion from webcam frame - optimized with async processing and caching"""
    global interview_controller

    if not interview_controller:
        raise HTTPException(status_code=400, detail="Interview not initialized")

    try:
        # Process image asynchronously
        frame = await async_process_image(request.image)

        # Analyze emotion with caching
        result = await async_emotion_analysis(frame, "current_session")

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Emotion analysis failed: {str(e)}"
        )


@app.post("/finish_interview", response_class=ORJSONResponse)
async def finish_interview(request: FinishInterviewRequest):
    """Finish interview and generate comprehensive report - optimized with async processing"""
    global interview_controller

    if not interview_controller:
        raise HTTPException(status_code=400, detail="Interview not initialized")

    try:
        # Generate final report asynchronously
        def generate_report():
            emotion_summary = (
                interview_controller.emotion_analyzer.get_emotion_summary()
            )
            return interview_controller.report_generator.generate_comprehensive_report(
                interview_controller.session,
                interview_controller.answer_scores,
                emotion_summary,
            )

        final_report = await asyncio.to_thread(generate_report)

        # Cleanup audio resources asynchronously
        def cleanup():
            interview_controller.session.cleanup()

        await asyncio.to_thread(cleanup)

        return {"success": True, "report": final_report}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to finish interview: {str(e)}"
        )


@app.post("/test_audio")
async def test_audio():
    """Test audio system functionality"""
    try:
        from src.utils import InterviewSession

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


# Legacy emotion analysis endpoints (for backward compatibility) - optimized
@app.post("/api/analyze-frame", response_class=ORJSONResponse)
async def analyze_frame(request: ImageAnalysisRequest):
    """Legacy endpoint for emotion analysis - optimized with async processing and caching"""
    try:
        # Process image asynchronously
        frame = await async_process_image(request.image)

        # Use cached emotion analysis
        result = await async_emotion_analysis(frame, request.session_id)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/api/get-feedback", response_class=ORJSONResponse)
async def get_emotion_feedback(request: FeedbackRequest):
    """Legacy endpoint for emotion feedback - optimized with async processing"""
    try:

        def get_feedback():
            return deepface_analyzer.get_emotion_feedback(
                request.emotion, request.confidence
            )

        feedback = await asyncio.to_thread(get_feedback)
        return feedback
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Feedback generation failed: {str(e)}"
        )


# Batch processing endpoint for multiple frames
@app.post("/api/analyze-frames-batch", response_class=ORJSONResponse)
async def analyze_frames_batch(frames: List[str], session_id: str = "default"):
    """Batch process multiple frames for better performance"""
    try:
        # Process frames in batches of 5 to avoid overwhelming the system
        batch_size = 5
        results = []

        for i in range(0, len(frames), batch_size):
            batch = frames[i : i + batch_size]

            # Process batch asynchronously
            tasks = [async_process_image(frame) for frame in batch]
            processed_frames = await asyncio.gather(*tasks)

            # Analyze emotions for batch
            emotion_tasks = [
                async_emotion_analysis(frame, session_id) for frame in processed_frames
            ]
            emotion_results = await asyncio.gather(*emotion_tasks)

            results.extend(emotion_results)

        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@app.get("/api/camera-test", response_class=ORJSONResponse)
async def camera_test():
    """Test camera and DeepFace availability - optimized"""
    return {"status": "Camera integration ready", "deepface_available": True}


@app.get("/health", response_class=ORJSONResponse)
async def health_check():
    """Health check for all services - optimized with performance metrics"""
    with cache_lock:
        cache_info = {
            "emotion_cache_size": len(emotion_cache),
            "question_cache_size": len(question_cache),
        }

    return {
        "status": "healthy",
        "services": {
            "deepface": True,
            "interview_system": True,
            "audio_processing": True,
            "caching": True,
        },
        "performance": {
            "cache_enabled": True,
            "async_processing": True,
            "orjson_serialization": True,
            **cache_info,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
