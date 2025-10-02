from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys, os

# Import SongManager from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.logic import SongManager

app = FastAPI(title="AI Powered Music Player", version="1.0")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

song_manager = SongManager()

# ------ Data Models --------
class SongCreate(BaseModel):
    name: str
    file_path: str
    duration: float

class SongRename(BaseModel):
    new_name: str

class SongPlayUpdate(BaseModel):
    new_play_count: int
    current_time: str

# ------------------- End Points -------------------------
@app.get("/")
def root():
    return {"message": "Welcome to the AI Powered Music Player API 🚀"}

@app.post("/songs")
def add_song(song: SongCreate):
    result = song_manager.add_song(song.name, song.file_path, song.duration)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.get("/songs")
def get_songs():
    result = song_manager.get_songs()
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.put("/songs/{song_id}/rename")
def rename_song(song_id: int, song: SongRename):
    result = song_manager.rename_song(song_id, song.new_name)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.put("/songs/{song_id}/playcount")
def update_play_count(song_id: int, update: SongPlayUpdate):
    result = song_manager.update_play_count(song_id, update.new_play_count, update.current_time)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.delete("/songs/{song_id}")
def delete_song(song_id: int):
    result = song_manager.delete_song(song_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)