from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
import httpx
import secrets
from urllib.parse import urlencode
from datetime import timedelta
from backend.config import Config
from backend.src.auth_utils import create_access_token
from backend.src.schemas import UserResponse
from backend.src.database import user_db

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/google/login")
async def google_login():
    params = {
        "client_id": Config.GOOGLE_CLIENT_ID,
        "redirect_uri": Config.GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
    }
    auth_url = f"{Config.GOOGLE_AUTHORIZE_URL}?{urlencode(params)}"
    return {"auth_url": auth_url}

@router.get("/github/login")
async def github_login():
    params = {
        "client_id": Config.GITHUB_CLIENT_ID,
        "redirect_uri": Config.GITHUB_REDIRECT_URI,
        "scope": "user:email",
    }
    auth_url = f"{Config.GITHUB_AUTHORIZE_URL}?{urlencode(params)}"
    return {"auth_url": auth_url}

@router.get("/google/callback")
async def google_callback(code: str):
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_data = {
                "client_id": Config.GOOGLE_CLIENT_ID,
                "client_secret": Config.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": Config.GOOGLE_REDIRECT_URI,
            }
            
            token_response = await client.post(Config.GOOGLE_TOKEN_URL, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            # Get user info
            headers = {"Authorization": f"Bearer {tokens['access_token']}"}
            user_response = await client.get(Config.GOOGLE_USER_INFO_URL, headers=headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Create user and JWT token
            user = user_db.create_user(
                email=user_data["email"],
                name=user_data["name"],
                provider="google",
                provider_id=user_data["id"]
            )
            
            access_token = create_access_token(data={"sub": user_data["email"]})
            redirect_url = f"{Config.FRONTEND_URL}/auth.html?token={access_token}"
            return RedirectResponse(url=redirect_url)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.get("/github/callback")
async def github_callback(code: str):
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_data = {
                "client_id": Config.GITHUB_CLIENT_ID,
                "client_secret": Config.GITHUB_CLIENT_SECRET,
                "code": code,
            }
            
            headers = {"Accept": "application/json"}
            token_response = await client.post(Config.GITHUB_TOKEN_URL, data=token_data, headers=headers)
            token_response.raise_for_status()
            tokens = token_response.json()
            
            # Get user info
            auth_headers = {"Authorization": f"token {tokens['access_token']}"}
            user_response = await client.get(Config.GITHUB_USER_INFO_URL, headers=auth_headers)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Get primary email
            email_response = await client.get(f"{Config.GITHUB_USER_INFO_URL}/emails", headers=auth_headers)
            email_response.raise_for_status()
            emails = email_response.json()
            primary_email = next((email["email"] for email in emails if email["primary"]), None)
            
            if not primary_email:
                raise HTTPException(status_code=400, detail="Could not retrieve email from GitHub")
            
            # Create user and JWT token
            user = user_db.create_user(
                email=primary_email,
                name=user_data.get("name", user_data["login"]),
                provider="github",
                provider_id=str(user_data["id"])
            )
            
            access_token = create_access_token(data={"sub": primary_email})
            redirect_url = f"{Config.FRONTEND_URL}/auth.html?token={access_token}"
            return RedirectResponse(url=redirect_url)
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str):
    from backend.src.auth_utils import verify_token
    
    email = verify_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = user_db.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        provider=user.provider,
        created_at=user.created_at
    )

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}