# Music Pad Images:

## Preview:

<img width="1920" height="1080" alt="preview" src="https://github.com/user-attachments/assets/c0089113-2270-4f60-a92d-5994534260f4" />

## PCB Schemat:

<img width="2030" height="1135" alt="image" src="https://github.com/user-attachments/assets/8210e1b6-5645-4bc8-bc43-de4861a928ab" />
<img width="2223" height="1112" alt="image" src="https://github.com/user-attachments/assets/298fdc92-edcf-4d9f-bddd-4171f73a7c21" />

## Case Schemat:

<img width="1878" height="1021" alt="image" src="https://github.com/user-attachments/assets/2e5a57ca-52a7-4bbb-9385-2812084bff3b" />
<img width="2256" height="1110" alt="image" src="https://github.com/user-attachments/assets/c5b0dd0f-ce2a-48be-9e2e-9ceab03c6849" />


#  Project Requirements

## File List
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
* **Programs:**
  * `code.py`
  * `libraries`

---

## Part List
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

Download CircuitPython for XIAO RP2040 from [circuitpython.org](https://circuitpython.org/board/seeeduino_xiao_rp2040/)
Double-press the reset button on your XIAO RP2040 to enter bootloader mode
A drive named RPI-RP2 will appear
Copy the downloaded .uf2 file to this drive
The board will restart and appear as CIRCUITPY

### 2. Install Required Libraries

Download the CircuitPython libraries
Copy these folders/files to the lib folder on your CIRCUITPY drive:

adafruit_hid/
adafruit_display_text/
adafruit_framebuf.mpy
adafruit_ssd1306.mpy

### 3. Upload Firmware

Copy the music_pad_firmware.py firmware to the root of your CIRCUITPY drive
The board will automatically restart
You should see "Music Pad" and "Loading..." on the OLED display

## 4. Wait for spotify to unlock the spotify for devs create app button, so i can make app for it.
