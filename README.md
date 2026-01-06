# Music Pad Preview:

<img width="1920" height="1080" alt="preview" src="https://github.com/user-attachments/assets/c0089113-2270-4f60-a92d-5994534260f4" />


##  Project Requirements

### File List
* **PCB Design:**
  * `Music Pad.kicad_pcb`
  * `Music Pad.kicad_sch`
  * `Music Pad.kicad_pro`
* **Case Design:**
  * `Bottom.step`
  * `Top.step`
* **Keyboard Layout Styles:**
  * `keyboard-layout.json`
  * `plate-2026-02-05T17_30_58.558Z.dxf`
  * `preview.png`
* **Music's Pad Firmware:**
  * `music_pad_firmware.py`
* **Computer Spotify Tracker:**
  * `spotify_monitor_app.py`

---

### Part List
| Quantity | Item | Notes |
| :--- | :--- | :--- |
| 1 | 3D Printed Case | Includes Bottom and Top files |
| 4 | M3x5mx4mm Heatset Inserts | |
| 4 | M3x16mm Screws | |
| 1 | 0.91 inch OLED Display | 4-pin version |
| 3 | DSA Keycaps | |
| 1 | Seeed XIAO RP2040 | |
| 3 | MX-Style Switches | |
| 1 | EC11 Rotary Encoder | |


## Setup Guide


### 1. Install CircuitPython

Download CircuitPython for XIAO RP2040 from circuitpython.org
Double-press the reset button on your XIAO RP2040 to enter bootloader mode
A drive named RPI-RP2 will appear
Copy the downloaded .uf2 file to this drive
The board will restart and appear as CIRCUITPY

### 2. Install Required Libraries

Download the CircuitPython library bundle from circuitpython.org/libraries (match your CircuitPython version)
Extract the bundle
Copy these folders/files to the lib folder on your CIRCUITPY drive:

adafruit_hid/ (entire folder)
adafruit_displayio_ssd1306.mpy
adafruit_display_text/ (entire folder)



### 3. Upload Firmware

Copy the music_pad_firmware.py firmware to the root of your CIRCUITPY drive
The board will automatically restart
You should see "Music Pad" and "Waiting for Spotify..." on the OLED display





## Part 2: Set Up Spotify API
### 1. Create Spotify Developer Account

Go to https://developer.spotify.com/dashboard
Log in with your Spotify account
Click "Create an App"
Fill in:

App name: Music Pad Monitor
App description: Monitors Spotify for Music Pad display
Accept the terms and click "Create"



### 2. Get Your Credentials

In your app dashboard, you'll see:

Client ID (copy this)
Click "Show Client Secret" and copy it


Click "Edit Settings"
Under "Redirect URIs", add: http://localhost:8888/callback
Click "Add" then "Save"


## Part 3: Install Windows Monitor App
### 1. Install Python

Download Python 3.8+ from python.org
During installation, check "Add Python to PATH"
Complete the installation

### 2. Install Required Packages
Open Command Prompt (cmd) and run:
bashpip install pyserial spotipy python-dotenv
### 3. Create Project Folder

Create a folder for your Music Pad monitor (e.g., C:\MusicPadMonitor)
Save the spotify_monitor_app.py file in this folder

### 4. Create Configuration File
Create a file named .env in the same folder with your credentials:
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
Replace your_client_id_here and your_client_secret_here with the values from your Spotify app.

## Part 4: Run the Monitor
### 1. Connect Your Music Pad

Connect your Music Pad to your computer via USB
Wait for Windows to recognize the device

### 2. Start the Monitor

Open Command Prompt
Navigate to your project folder:

bash   cd C:\MusicPadMonitor

Run the monitor:

bash   python spotify_monitor_app.py
### 3. First Time Setup

The first time you run it, a browser window will open
Log in to Spotify and authorize the app
The browser will redirect to a page that may show "can't reach this page" - that's OK!
Copy the entire URL from the address bar
Paste it into the Command Prompt when asked
Press Enter
