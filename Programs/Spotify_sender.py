import spotipy
from spotipy.oauth2 import SpotifyOAuth
import serial
import time
import os

# ── Spotify credentials ──────────────────────────────────────────────
SPOTIPY_CLIENT_ID     = "PLACE YOUR SPOTIFY CLIENT ID HERE"
SPOTIPY_CLIENT_SECRET = "PLACE YOUR SPOTIFY CLIENT SECRET HERE"
SPOTIPY_REDIRECT_URI  = "http://127.0.0.1:8888/callback"

# ── Cache path ───────────────────────────────────────────────────────
cache_path = os.path.join(os.path.expanduser("~"), "Desktop", ".spotify_cache")

# ── Serial setup ─────────────────────────────────────────────────────
port = "COM9"
print(f"Connecting to {port}...")
ser = serial.Serial(port, 115200, timeout=1)
time.sleep(2)
print("Connected!")

# ── Spotify setup ────────────────────────────────────────────────────
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-read-currently-playing user-read-playback-state",
    cache_path=cache_path,
    open_browser=True
))

# ── Function definition ──────────────────────────────────────────────
def get_now_playing():
    try:
        result = sp.currently_playing()
        if result and result["is_playing"] and result["item"]:
            track  = result["item"]["name"]
            artist = result["item"]["artists"][0]["name"]
            return f"{track} - {artist}"
        else:
            return "Paused"
    except Exception as e:
        print(f"Spotify error: {e}")
        return None

# ── Main loop ────────────────────────────────────────────────────────
last_track = ""
POLL_INTERVAL = 3
last_send_time = 0

while True:
    current_time = time.time()
    track_info = get_now_playing()
    print(f"Track: {track_info}")

    if track_info and (track_info != last_track or current_time - last_send_time >= 2):
        print(f"Sending: {track_info}")
        ser.write((track_info + "\n").encode("utf-8"))
        last_track = track_info
        last_send_time = current_time

    time.sleep(POLL_INTERVAL)
