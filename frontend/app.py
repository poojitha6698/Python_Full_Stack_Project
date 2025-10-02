# frontend/app.py
import streamlit as st
import requests
import datetime
from supabase import create_client
from dotenv import load_dotenv
import os
import io
import uuid

# ----------------- Load Environment Variables -----------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

API_URL = "http://127.0.0.1:8000"  # FastAPI backend URL

st.set_page_config(page_title="AI Music Player", layout="wide")
st.title("🎵 AI-Powered Music Player (Supabase Storage)")

# ----------------- Upload Song -----------------
st.header("Upload a Song")
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav"])
song_name = st.text_input("Song Name")

if uploaded_file and song_name:
    if st.button("Upload Song to Supabase"):
        # ✅ Generate a unique filename to avoid duplicates
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        file_path = f"songs/{unique_filename}"

        try:
            # Upload file to Supabase
            supabase.storage.from_("songs").upload(file_path, uploaded_file.getvalue())

            # Get public URL
            file_url_dict = supabase.storage.from_("songs").get_public_url(file_path)
            file_url = file_url_dict.get("publicUrl")

            # Calculate duration
            try:
                from mutagen.mp3 import MP3
                audio = MP3(io.BytesIO(uploaded_file.getvalue()))
                duration = audio.info.length
            except Exception:
                duration = 0.0

            # Send metadata to FastAPI backend
            data = {
                "name": song_name,
                "file_path": file_url,
                "duration": duration
            }
            response = requests.post(f"{API_URL}/songs", json=data)
            if response.status_code == 200:
                st.success("✅ Song uploaded successfully!")
            else:
                st.error(f"Error saving song metadata: {response.text}")

        except Exception as e:
            st.error(f"❌ Upload failed: {e}")

# ----------------- Display Songs -----------------
st.header("All Songs")
try:
    response = requests.get(f"{API_URL}/songs")
    if response.status_code == 200:
        songs = response.json().get("songs", [])
    else:
        songs = []
        st.error("Failed to fetch songs.")
except Exception:
    songs = []
    st.error("Backend not running.")

for song in songs:
    st.subheader(song["name"])
    col1, col2, col3 = st.columns([3, 1, 1])

    # Play button
    with col1:
        if song.get("file_path"):
            st.audio(song["file_path"])
        else:
            st.info("No file available for this song.")

    # Rename song
    with col2:
        new_name = st.text_input(f"Rename {song['name']}", key=f"rename_{song['id']}")
        if st.button("Rename", key=f"rename_btn_{song['id']}"):
            payload = {"new_name": new_name}
            res = requests.put(f"{API_URL}/songs/{song['id']}/rename", json=payload)
            if res.status_code == 200:
                st.success("✅ Song renamed!")
            else:
                st.error("Failed to rename song.")

    # Delete song
    with col3:
        if st.button("Delete", key=f"delete_{song['id']}"):
            res = requests.delete(f"{API_URL}/songs/{song['id']}")
            if res.status_code == 200:
                st.success("✅ Song deleted!")
            else:
                st.error("Failed to delete song.")

# ----------------- Simulate Play -----------------
st.header("Simulate Play Count")
song_id_play = st.selectbox(
    "Select Song ID to simulate play",
    options=[s["id"] for s in songs] if songs else []
)
if st.button("Play Song"):
    current_time = datetime.datetime.now().isoformat()
    song_obj = next((s for s in songs if s["id"] == song_id_play), None)
    if song_obj:
        payload = {
            "new_play_count": song_obj.get("play_count", 0) + 1,
            "current_time": current_time
        }
        res = requests.put(f"{API_URL}/songs/{song_id_play}/playcount", json=payload)
        if res.status_code == 200:
            st.success("✅ Play count updated!")
        else:
            st.error("Failed to update play count.")