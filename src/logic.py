# src/logic.py
from src.db import DatabaseManager

class SongManager:
    """
    Business logic layer – bridges FastAPI/Streamlit frontend with the database.
    """

    def __init__(self):
        self.db = DatabaseManager()

    # ----- Create -----
    def add_song(self, name: str, file_path: str, duration: float):
        if not name or not file_path or not duration:
            return {"success": False, "message": "All fields are required"}

        try:
            result = self.db.create_song(name, file_path, duration)
            if getattr(result, "error", None) is None:
                return {"success": True, "message": "Song added successfully", "data": result.data}
            return {"success": False, "message": f"Supabase Error: {result.error}"}
        except Exception as e:
            return {"success": False, "message": f"Exception in add_song: {str(e)}"}

    # ----- Read -----
    def get_songs(self):
        try:
            result = self.db.get_all_songs()
            if getattr(result, "error", None) is None:
                return {"success": True, "songs": result.data}
            return {"success": False, "message": f"Supabase Error: {result.error}"}
        except Exception as e:
            return {"success": False, "message": f"Exception in get_songs: {str(e)}"}

    # ----- Update: Rename -----
    def rename_song(self, song_id: int, new_name: str):
        try:
            result = self.db.update_song_name(song_id, new_name)
            if getattr(result, "error", None) is None:
                return {"success": True, "message": f"Song {song_id} renamed successfully"}
            return {"success": False, "message": f"Supabase Error: {result.error}"}
        except Exception as e:
            return {"success": False, "message": f"Exception in rename_song: {str(e)}"}

    # ----- Update: Play Count -----
    def update_play_count(self, song_id: int, new_play_count: int, current_time: str):
        try:
            result = self.db.update_play_count(song_id, new_play_count, current_time)
            if getattr(result, "error", None) is None:
                return {"success": True, "message": f"Play count updated for song {song_id}"}
            return {"success": False, "message": f"Supabase Error: {result.error}"}
        except Exception as e:
            return {"success": False, "message": f"Exception in update_play_count: {str(e)}"}

    # ----- Delete -----
    def delete_song(self, song_id: int):
        try:
            result = self.db.delete_song(song_id)
            if getattr(result, "error", None) is None:
                return {"success": True, "message": f"Song {song_id} deleted successfully"}
            return {"success": False, "message": f"Supabase Error: {result.error}"}
        except Exception as e:
            return {"success": False, "message": f"Exception in delete_song: {str(e)}"}