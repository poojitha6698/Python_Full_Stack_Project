from src.db import DatabaseManager

class SongManager:
    """
    Business logic layer – bridges FastAPI/Streamlit frontend with the database.
    """

    def __init__(self):
        self.db = DatabaseManager()

    # helper to extract data / error from supabase response or dict-like response
    def _extract(self, resp):
        # resp may be an object with .data and .error, or a dict with keys "data"/"error",
        # or some other shape. Return tuple (data, error)
        data = None
        error = None

        if resp is None:
            return None, "No response"

        # attribute style (objects)
        if hasattr(resp, "data") or hasattr(resp, "error"):
            data = getattr(resp, "data", None)
            error = getattr(resp, "error", None)
            return data, error

        # dict-style
        if isinstance(resp, dict):
            data = resp.get("data") or resp.get("body") or resp.get("result") or resp.get("records") or resp.get("rows")
            # fallback to entire resp if it looks like data
            if data is None and any(k in resp for k in ("name", "file_path", "duration", "play_count")):
                data = resp
            error = resp.get("error")
            return data, error

        # tuple (data, error)
        if isinstance(resp, tuple) and len(resp) == 2:
            return resp[0], resp[1]

        # fallback
        return resp, None

    # ----- Create -----
    def add_song(self, name: str, file_path: str, duration: float):
        if not name or not file_path:
            return {"success": False, "message": "All fields are required"}

        try:
            result = self.db.create_song(name, file_path, duration)
            data, error = self._extract(result)
            if not error:
                return {"success": True, "message": "Song added successfully", "data": data}
            return {"success": False, "message": f"Supabase Error: {error}"}
        except Exception as e:
            return {"success": False, "message": f"Exception in add_song: {str(e)}"}

    # ----- Read -----
    def get_songs(self):
        try:
            result = self.db.get_all_songs()
            data, error = self._extract(result)
            if not error:
                # ensure we return a list
                songs = data if isinstance(data, list) else (data.get("data") if isinstance(data, dict) and data.get("data") else data)
                if songs is None:
                    songs = []
                return {"success": True, "songs": songs}
            return {"success": False, "message": f"Supabase Error: {error}"}
        except Exception as e:
            return {"success": False, "message": f"Exception in get_songs: {str(e)}"}

    # ----- Update: Rename -----
    def rename_song(self, song_id: int, new_name: str):
        try:
            result = self.db.update_song_name(song_id, new_name)
            _, error = self._extract(result)
            if not error:
                return {"success": True, "message": f"Song {song_id} renamed successfully"}
            return {"success": False, "message": f"Supabase Error: {error}"}
        except Exception as e:
            return {"success": False, "message": f"Exception in rename_song: {str(e)}"}

    # ----- Update: Play Count -----
    def update_play_count(self, song_id: int, new_play_count: int, current_time: str):
        try:
            result = self.db.update_play_count(song_id, new_play_count, current_time)
            _, error = self._extract(result)
            if not error:
                return {"success": True, "message": f"Play count updated for song {song_id}"}
            return {"success": False, "message": f"Supabase Error: {error}"}
        except Exception as e:
            return {"success": False, "message": f"Exception in update_play_count: {str(e)}"}

    # ----- Delete -----
    def delete_song(self, song_id: int):
        try:
            result = self.db.delete_song(song_id)
            _, error = self._extract(result)
            if not error:
                return {"success": True, "message": f"Song {song_id} deleted successfully"}
            return {"success": False, "message": f"Supabase Error: {error}"}
        except Exception as e:
            return {"success": False, "message": f"Exception in delete_song: {str(e)}"}
