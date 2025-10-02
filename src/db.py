# src/db.py
import os
from supabase import create_client
from dotenv import load_dotenv

# ---------------- Load ENV ----------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Missing SUPABASE_URL or SUPABASE_KEY in .env file")

# ---------------- Client ----------------
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class DatabaseManager:
    """Handles all database CRUD operations with Supabase"""

    # Create Song
    def create_song(self, name: str, file_path: str, duration: float):
        try:
            result = supabase.table("songs").insert({
                "name": name,
                "file_path": file_path,
                "duration": duration,
            }).execute()
            print("DEBUG: create_song result:", result)
            return result
        except Exception as e:
            print("❌ ERROR in create_song:", e)
            raise

    # Get all Songs (ordered by last_played, newest first)
    def get_all_songs(self):
        try:
            result = supabase.table("songs").select("*").order("last_played", desc=True).execute()
            print("DEBUG: get_all_songs result:", result)
            return result
        except Exception as e:
            print("❌ ERROR in get_all_songs:", e)
            raise

    # Update Song name
    def update_song_name(self, song_id: int, new_name: str):
        try:
            result = supabase.table("songs").update({"name": new_name}).eq("id", song_id).execute()
            print("DEBUG: update_song_name result:", result)
            return result
        except Exception as e:
            print("❌ ERROR in update_song_name:", e)
            raise

    # Update Play Count & Last Played time
    def update_play_count(self, song_id: int, new_play_count: int, current_time: str):
        try:
            result = supabase.table("songs").update({
                "play_count": new_play_count,
                "last_played": current_time
            }).eq("id", song_id).execute()
            print("DEBUG: update_play_count result:", result)
            return result
        except Exception as e:
            print("❌ ERROR in update_play_count:", e)
            raise

    # Delete Song
    def delete_song(self, song_id: int):
        try:
            result = supabase.table("songs").delete().eq("id", song_id).execute()
            print("DEBUG: delete_song result:", result)
            return result
        except Exception as e:
            print("❌ ERROR in delete_song:", e)
            raise