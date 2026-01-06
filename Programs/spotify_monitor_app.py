"""
Spotify Monitor for Music Pad
This application monitors Spotify on Windows and sends track info to the Music Pad via serial.

Requirements:
pip install pyserial spotipy python-dotenv

Setup:
1. Create a Spotify App at https://developer.spotify.com/dashboard
2. Get your Client ID and Client Secret
3. Create a .env file with:
   SPOTIPY_CLIENT_ID=your_client_id
   SPOTIPY_CLIENT_SECRET=your_client_secret
   SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
"""

import serial
import serial.tools.list_ports
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify API setup
SCOPE = "user-read-currently-playing user-read-playback-state"

class SpotifyMonitor:
    def __init__(self):
        self.serial_port = None
        self.spotify = None
        self.last_track = None
        self.last_artist = None
        
    def find_music_pad(self):
        """Find the Music Pad serial port"""
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Look for the XIAO RP2040 (usually shows as USB Serial Device)
            if "USB" in port.description or "Serial" in port.description:
                try:
                    print(f"Trying port: {port.device} - {port.description}")
                    ser = serial.Serial(port.device, 115200, timeout=1)
                    time.sleep(2)  # Wait for connection to establish
                    print(f"Connected to Music Pad on {port.device}")
                    return ser
                except Exception as e:
                    print(f"Could not connect to {port.device}: {e}")
        return None
    
    def connect_spotify(self):
        """Connect to Spotify API"""
        try:
            self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIPY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
                scope=SCOPE,
                cache_path=".spotify_cache"
            ))
            print("Connected to Spotify API")
            return True
        except Exception as e:
            print(f"Error connecting to Spotify: {e}")
            return False
    
    def get_current_track(self):
        """Get currently playing track from Spotify"""
        try:
            current = self.spotify.current_playback()
            if current and current['is_playing']:
                item = current['item']
                if item:
                    track_name = item['name']
                    artist_name = item['artists'][0]['name']
                    return track_name, artist_name
            return None, None
        except Exception as e:
            print(f"Error getting track: {e}")
            return None, None
    
    def send_to_device(self, message):
        """Send message to Music Pad"""
        if self.serial_port:
            try:
                self.serial_port.write((message + '\n').encode('utf-8'))
                self.serial_port.flush()
            except Exception as e:
                print(f"Error sending to device: {e}")
                self.serial_port = None
    
    def run(self):
        """Main monitoring loop"""
        print("Starting Spotify Monitor for Music Pad...")
        print("=" * 50)
        
        # Connect to Music Pad
        self.serial_port = self.find_music_pad()
        if not self.serial_port:
            print("\nERROR: Could not find Music Pad!")
            print("Make sure your Music Pad is connected via USB.")
            return
        
        # Connect to Spotify
        if not self.connect_spotify():
            print("\nERROR: Could not connect to Spotify!")
            print("Make sure you've set up your .env file correctly.")
            return
        
        print("\nMonitoring started! Track info will be sent to your Music Pad.")
        print("Press Ctrl+C to stop.\n")
        
        try:
            while True:
                track, artist = self.get_current_track()
                
                if track and artist:
                    # Check if track changed
                    if track != self.last_track or artist != self.last_artist:
                        display_text = f"{track} - {artist}"
                        print(f"Now Playing: {display_text}")
                        self.send_to_device(display_text)
                        self.last_track = track
                        self.last_artist = artist
                elif self.last_track is not None:
                    # Playback stopped
                    print("Playback stopped")
                    self.send_to_device("Spotify paused")
                    self.last_track = None
                    self.last_artist = None
                
                time.sleep(1)  # Check every second
                
        except KeyboardInterrupt:
            print("\n\nStopping monitor...")
        finally:
            if self.serial_port:
                self.serial_port.close()
            print("Disconnected from Music Pad")

if __name__ == "__main__":
    monitor = SpotifyMonitor()
    monitor.run()
