from src.db import DatabaseManager

class SongManager:
    """
    Acts as a bridge between frontend (Streamlit/FastAPI) and the database.
    Provides business logic for handling songs.
    """

    def __init__(self):
        # Create a DatabaseManager instance (handles actual DB operations)
        self.db = DatabaseManager()

    # ----- Create -----
    def add_song(self, name: str, file_path: str, duration: float):
        if not name or not file_path or not duration:
            return {"success": False, "message": "All fields are required"}

        result = self.db.create_song(name, file_path, duration)

        if result.error is None:
            return {"success": True, "message": "Song added successfully"}
        return {"success": False, "message": f"Error: {result.error}"}

    # ----- Read -----
    def get_songs(self):
        result = self.db.get_all_songs()

        if result.error is None:
            return {"success": True, "songs": result.data}
        return {"success": False, "message": f"Error: {result.error}"}

    # ----- Update: Rename -----
    def rename_song(self, song_id: int, new_name: str):
        result = self.db.update_song_name(song_id, new_name)

        if result.error is None:
            return {"success": True, "message": f"Song {song_id} renamed successfully"}
        return {"success": False, "message": f"Error: {result.error}"}

    # ----- Update: Play Count -----
    def update_play_count(self, song_id: int, new_play_count: int, current_time: str):
        result = self.db.update_play_count(song_id, new_play_count, current_time)

        if result.error is None:
            return {"success": True, "message": f"Play count updated for song {song_id}"}
        return {"success": False, "message": f"Error: {result.error}"}

    # ----- Delete -----
    def delete_song(self, song_id: int):
        result = self.db.delete_song(song_id)

        if result.error is None:
            return {"success": True, "message": f"Song {song_id} deleted successfully"}
        return {"success": False, "message": f"Error: {result.error}"}
