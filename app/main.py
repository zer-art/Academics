from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.services.vision.deepface import deepface_analyzer

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
class ImageAnalysisRequest(BaseModel):
    image: str  # base64 encoded image
    session_id: str = "default"

class FeedbackRequest(BaseModel):
    emotion: str
    confidence: float

# Serve static assets from landing directory
app.mount("/assets", StaticFiles(directory="landing/assets"), name="assets")

@app.get("/", response_class=FileResponse)
async def index(): 
    return FileResponse("landing/index.html")

@app.get("/interview")
async def interview_page(request: Request):
    context = {
        "request": request,
        "title": "AI Interview Coach - Interview Session",
    }
    return templates.TemplateResponse("interview.html", context)

@app.post("/api/analyze-frame")
async def analyze_frame(request: ImageAnalysisRequest):
    try:
        result = deepface_analyzer.analyze_base64_image(request.image)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/get-feedback")
async def get_emotion_feedback(request: FeedbackRequest):
    try:
        feedback = deepface_analyzer.get_emotion_feedback(request.emotion, request.confidence)
        return JSONResponse(content=feedback)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback generation failed: {str(e)}")

@app.get("/api/camera-test")
async def camera_test():

    return {"status": "Camera integration ready", "deepface_available": True}


