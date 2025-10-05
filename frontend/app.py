import streamlit as st
import requests
import datetime
from supabase import create_client
from dotenv import load_dotenv
import os
import io
import uuid

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Missing SUPABASE_URL or SUPABASE_KEY in environment.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Music Player", layout="wide")
st.title("🎵 AI-Powered Music Player (Supabase Storage)")

def _parse_supabase_response(resp):
    """
    Normalize responses from supabase Python client. Return dict with keys 'data' and 'error'.
    """
    if resp is None:
        return {"data": None, "error": "No response"}

    if isinstance(resp, dict):
        # common shapes: {'data': ..., 'error': ...} or {'publicUrl': '...'}
        return {"data": resp.get("data", resp.get("data", None) or resp), "error": resp.get("error")}
    if hasattr(resp, "data") or hasattr(resp, "error"):
        return {"data": getattr(resp, "data", None), "error": getattr(resp, "error", None)}
    if isinstance(resp, tuple) and len(resp) == 2:
        return {"data": resp[0], "error": resp[1]}
    # fallback
    return {"data": resp, "error": None}


def _get_public_url_safe(bucket: str, path: str):
    """
    Handles multiple return shapes from get_public_url; falls back to constructing the public URL.
    """
    try:
        url_resp = supabase.storage.from_(bucket).get_public_url(path)
    except Exception as e:
        url_resp = None

    # If it's a plain string (some client versions), accept it
    if isinstance(url_resp, str):
        return url_resp

    # If the client returns dict/object, try common keys
    if isinstance(url_resp, dict):
        for key in ("publicUrl", "public_url", "publicURL", "url"):
            if key in url_resp and url_resp[key]:
                return url_resp[key]
        # nested 'data'
        if "data" in url_resp and isinstance(url_resp["data"], dict):
            for key in ("publicUrl", "public_url", "url"):
                if key in url_resp["data"] and url_resp["data"][key]:
                    return url_resp["data"][key]

    # If it's an object with .data or similar
    if hasattr(url_resp, "data"):
        d = getattr(url_resp, "data", None)
        if isinstance(d, dict):
            for key in ("publicUrl", "public_url", "url"):
                if key in d and d[key]:
                    return d[key]

    # Final fallback: construct the public URL directly using Supabase storage public path
    # Pattern: https://<project>.supabase.co/storage/v1/object/public/<bucket>/<file_path>
    base = SUPABASE_URL.rstrip("/")
    constructed = f"{base}/storage/v1/object/public/{bucket}/{path}"
    return constructed

# ----------------- Upload Song -----------------
st.header("Upload a Song")
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav"])
song_name = st.text_input("Song Name")

if uploaded_file and song_name:
    if st.button("Upload Song to Supabase"):
        unique_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
        file_path = f"songs/{unique_filename}"

        try:
            file_bytes = uploaded_file.getvalue()
            upload_resp = supabase.storage.from_("songs").upload(file_path, file_bytes)
            upload_parsed = _parse_supabase_response(upload_resp)
            if upload_parsed.get("error"):
                st.error(f"Upload failed: {upload_parsed.get('error')}")
            else:
                # Try to get public url in a robust way
                file_url = _get_public_url_safe("songs", file_path)

                # Calculate duration (best-effort)
                try:
                    from mutagen.mp3 import MP3
                    audio = MP3(io.BytesIO(file_bytes))
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
                if response.ok:
                    st.success("✅ Song uploaded successfully!")
                else:
                    st.error(f"Error saving song metadata: {response.text}")

        except Exception as e:
            st.error(f"❌ Upload failed: {e}")

# ----------------- Display Songs -----------------
st.header("All Songs")
try:
    response = requests.get(f"{API_URL}/songs")
    songs = []
    if response.ok:
        payload = response.json()
        # API returns {"success": True, "songs": [...]}
        songs = payload.get("songs") or payload.get("data") or []
    else:
        st.error("Failed to fetch songs from backend.")
except Exception:
    songs = []
    st.error("Backend not running or unreachable.")

for song in songs:
    st.subheader(song.get("name", "(no name)"))
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        file_path = song.get("file_path")
        if file_path:
            # st.audio accepts URL or bytes
            st.audio(file_path)
        else:
            st.info("No file available for this song.")

    with col2:
        new_name = st.text_input(f"Rename {song.get('name')}", key=f"rename_{song.get('id')}")
        if st.button("Rename", key=f"rename_btn_{song.get('id')}"):
            payload = {"new_name": new_name}
            res = requests.put(f"{API_URL}/songs/{song.get('id')}/rename", json=payload)
            if res.ok:
                st.success("✅ Song renamed!")
            else:
                st.error(f"Failed to rename song: {res.text}")

    with col3:
        if st.button("Delete", key=f"delete_{song.get('id')}"):
            res = requests.delete(f"{API_URL}/songs/{song.get('id')}")
            if res.ok:
                st.success("✅ Song deleted!")
            else:
                st.error(f"Failed to delete song: {res.text}")

# ----------------- Simulate Play -----------------
st.header("Simulate Play Count")
if songs:
    options = [s.get("id") for s in songs]
    song_id_play = st.selectbox("Select Song ID to simulate play", options=options)
    if st.button("Play Song"):
        current_time = datetime.datetime.now().isoformat()
        song_obj = next((s for s in songs if s.get("id") == song_id_play), None)
        if song_obj:
            payload = {
                "new_play_count": (song_obj.get("play_count") or 0) + 1,
                "current_time": current_time
            }
            res = requests.put(f"{API_URL}/songs/{song_id_play}/playcount", json=payload)
            if res.ok:
                st.success("✅ Play count updated!")
            else:
                st.error(f"Failed to update play count: {res.text}")
