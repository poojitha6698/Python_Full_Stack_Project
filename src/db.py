import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

class DatabaseManager:
    # Create Song
    def create_song(name: str, file_path: str, duration: float):
        return supabase.table("songs").insert({
             "name": name,
            "file_path": file_path,
            "duration": duration,
        }).execute()

    # Get all Songs (ordered by last_played, newest first)
    def get_all_songs():
        return supabase.table("songs").select("*").order("last_played", desc=True).execute()

    # Update Song name
    def update_song_name(song_id: int, new_name: str):
        return supabase.table("songs").update({"name": new_name}).eq("id", song_id).execute()

    # Update Play Count & Last Played time
    def update_play_count(song_id: int, new_play_count: int, current_time: str):
        return supabase.table("songs").update({
            "play_count": new_play_count,
            "last_played": current_time
        }).eq("id", song_id).execute()

    # Delete Song
    def delete_song(song_id: int):
        return supabase.table("songs").delete().eq("id", song_id).execute()
