from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import httpx
from auth import get_current_user, get_current_active_user
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Friendly Video Sphere API",
    description="Backend API for Friendly Video Sphere application",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Root endpoint redirects to API documentation
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/api/docs")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Frontend URL
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
        "https://*.clerk.accounts.dev"  # Clerk auth domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class User(BaseModel):
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None

class Video(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    url: str
    user_id: Optional[str] = None

# In-memory storage (replace with database in production)
db: List[Video] = [
    Video(id=1, title="Sample Video 1", description="This is a sample video", url="https://example.com/video1", user_id="user_123"),
    Video(id=2, title="Sample Video 2", description="Another sample video", url="https://example.com/video2", user_id="user_123"),
]

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Auth endpoints
@app.get("/api/auth/me", response_model=User)
async def get_current_user_endpoint(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current authenticated user"""
    return current_user

# Video endpoints
@app.get("/api/videos", response_model=List[Video])
async def get_videos():
    """Get all videos (public)"""
    return db

@app.get("/api/videos/me", response_model=List[Video])
async def get_my_videos(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get videos for the current user"""
    user_id = current_user.get("sub")
    return [video for video in db if video.user_id == user_id]

@app.get("/api/videos/{video_id}", response_model=Video)
async def get_video(video_id: int):
    """Get a single video by ID (public)"""
    video = next((v for v in db if v.id == video_id), None)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@app.post("/api/videos", response_model=Video, status_code=status.HTTP_201_CREATED)
async def create_video(
    video: Video,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new video (protected)"""
    video.user_id = current_user.get("sub")
    db.append(video)
    return video

@app.delete("/api/videos/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a video (protected, owner only)"""
    user_id = current_user.get("sub")
    global db
    video_index = next((i for i, v in enumerate(db) if v.id == video_id and v.user_id == user_id), None)
    
    if video_index is None:
        raise HTTPException(status_code=404, detail="Video not found or not authorized")
    
    db.pop(video_index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
