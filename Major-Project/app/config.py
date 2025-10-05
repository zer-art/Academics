import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # JWT Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # OAuth Settings
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
    )

    GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    GITHUB_REDIRECT_URI = os.getenv(
        "GITHUB_REDIRECT_URI", "http://localhost:8000/auth/github/callback"
    )

    # Frontend URL
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8000")

    # OAuth URLs
    GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
    GITHUB_USER_INFO_URL = "https://api.github.com/user"

    # llm settings
    # Accept multiple env var names for the Gemini API key
    GEMINI = (
        os.getenv("GEMINI") or os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY")
    )
    # Default Gemini model; make configurable via GEMINI_MODEL env var
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    # Assembly AI API key (accept common env names)
    ASSEMBLY_AI = (
        os.getenv("ASSEMBLY_AI")
        or os.getenv("ASSEMBLY_AI_API_KEY")
        or os.getenv("ASSEMBLY_AI_KEY")
    )


# Make GEMINI available as module-level variable for imports
# Make GEMINI available as module-level variable for imports
GEMINI = Config.GEMINI
# Expose GEMINI_MODEL and GEMINI_API_KEY aliases
GEMINI_MODEL = Config.GEMINI_MODEL
# Make ASSEMBLY_AI available at module level too
ASSEMBLY_AI = Config.ASSEMBLY_AI
