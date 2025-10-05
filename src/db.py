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

    def create_song(self, name: str, file_path: str, duration: float):
        try:
            result = supabase.table("songs").insert({
                "name": name,
                "file_path": file_path,
                "duration": duration,
            }).execute()
            return result
        except Exception as e:
            print("❌ ERROR in create_song:", e)
            raise

    def get_all_songs(self):
        try:
            result = supabase.table("songs").select("*").order("last_played", desc=True).execute()
            return result
        except Exception as e:
            print("❌ ERROR in get_all_songs:", e)
            raise

    def update_song_name(self, song_id: int, new_name: str):
        try:
            result = supabase.table("songs").update({"name": new_name}).eq("id", song_id).execute()
            return result
        except Exception as e:
            print("❌ ERROR in update_song_name:", e)
            raise

    def update_play_count(self, song_id: int, new_play_count: int, current_time: str):
        try:
            result = supabase.table("songs").update({
                "play_count": new_play_count,
                "last_played": current_time
            }).eq("id", song_id).execute()
            return result
        except Exception as e:
            print("❌ ERROR in update_play_count:", e)
            raise

    def delete_song(self, song_id: int):
        try:
            result = supabase.table("songs").delete().eq("id", song_id).execute()
            return result
        except Exception as e:
            print("❌ ERROR in delete_song:", e)
            raise
