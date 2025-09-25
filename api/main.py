# Frontend --------> API --------> logic --------> db --------> Response
# api/main.py

# api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys, os

# Import SongManager from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logic import SongManager


# ---------------- App Setup -----------------------------

app = FastAPI(title="AI Powered Music Player", version="1.0")

# ---------------- Allow Frontend (Streamlit/React) to call the API ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (frontend apps)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a SongManager instance (business logic)
song_manager = SongManager()


# ------ Data Models --------

class SongCreate(BaseModel):
    """
    Schema for creating a song
    """
    name: str
    file_path: str
    duration: float


class SongRename(BaseModel):
    """
    Schema for renaming a song
    """
    new_name: str


class SongPlayUpdate(BaseModel):
    """
    Schema for updating play count and last played time
    """
    new_play_count: int
    current_time: str


# ------------------- End Points -------------------------

@app.get("/")
def root():
    return {"message": "Welcome to the AI Powered Music Player API 🚀"}


# ----- Create -----
@app.post("/songs")
def add_song(song: SongCreate):
    """Add a new song"""
    result = song_manager.add_song(song.name, song.file_path, song.duration)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ----- Read -----
@app.get("/songs")
def get_songs():
    """Fetch all songs"""
    result = song_manager.get_songs()
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ----- Update: Rename -----
@app.put("/songs/{song_id}/rename")
def rename_song(song_id: int, song: SongRename):
    """Rename a song"""
    result = song_manager.rename_song(song_id, song.new_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ----- Update: Play Count -----
@app.put("/songs/{song_id}/playcount")
def update_play_count(song_id: int, update: SongPlayUpdate):
    """Update play count and last played time"""
    result = song_manager.update_play_count(song_id, update.new_play_count, update.current_time)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# ----- Delete -----
@app.delete("/songs/{song_id}")
def delete_song(song_id: int):
    """Delete a song"""
    result = song_manager.delete_song(song_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


# --------- Run ------------------

if __name__ == "__main__":
    import uvicorn 
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)