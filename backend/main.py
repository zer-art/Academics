from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.routers import auth

app = FastAPI(title="Aivox.io")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

# Serve static files (frontend assets)
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

@app.get("/" , response_class=FileResponse)
async def index(): 
    return FileResponse("frontend/index.html")

@app.get("/auth", response_class=FileResponse)
async def auth_page():
    return FileResponse("frontend/auth.html")

@app.get("/interview", response_class=FileResponse)
async def interview_page():
    return FileResponse("frontend/interview.html")



