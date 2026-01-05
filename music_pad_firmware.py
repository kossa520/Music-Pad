import board
import digitalio
import rotaryio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
import time
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_displayio_ssd1306
import usb_cdc

# Release any previously used displays
displayio.release_displays()

# Initialize I2C for OLED
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)

# Create the display (128x32 OLED)
WIDTH = 128
HEIGHT = 32
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Initialize Consumer Control (for media keys)
cc = ConsumerControl(usb_hid.devices)

# Initialize USB Serial
serial = usb_cdc.data

# Configure GPIO pins for switches based on schematic
switch1_pin = board.D0  # GPIO26 - Play/Pause
switch2_pin = board.D1  # GPIO27 - Next Track
switch3_pin = board.D2  # GPIO28 - Previous Track

# Setup switches with pull-up resistors
switch1 = digitalio.DigitalInOut(switch1_pin)
switch1.direction = digitalio.Direction.INPUT
switch1.pull = digitalio.Pull.UP

switch2 = digitalio.DigitalInOut(switch2_pin)
switch2.direction = digitalio.Direction.INPUT
switch2.pull = digitalio.Pull.UP

switch3 = digitalio.DigitalInOut(switch3_pin)
switch3.direction = digitalio.Direction.INPUT
switch3.pull = digitalio.Pull.UP

# Setup rotary encoder
encoder = rotaryio.IncrementalEncoder(board.D3, board.D4)

# Variables for switch debouncing
switch1_pressed = False
switch2_pressed = False
switch3_pressed = False
debounce_time = 0.2
last_press_time = [0, 0, 0]

# Variable for encoder position
last_position = encoder.position

# Setup display with scrolling text support
splash = displayio.Group()
display.root_group = splash

# Create text labels
title_label = label.Label(terminalio.FONT, text="Music Pad", color=0xFFFFFF, x=35, y=5)
splash.append(title_label)

# Track info label (will scroll if too long)
track_label = label.Label(terminalio.FONT, text="Waiting...", color=0xFFFFFF, x=0, y=20)
splash.append(track_label)

# Scrolling variables
scroll_position = 0
scroll_delay = 0
scroll_speed = 3  # frames between scroll steps
current_track = "Waiting for Spotify..."
last_track_update = time.monotonic()

def update_track_display(text):
    """Update the track text on the display with scrolling support"""
    global current_track, scroll_position, last_track_update
    if text != current_track:
        current_track = text
        scroll_position = 0
        last_track_update = time.monotonic()

def scroll_text():
    """Handle text scrolling if the text is too long"""
    global scroll_position, scroll_delay
    
    # Calculate if text needs scrolling (roughly 21 characters fit on screen)
    max_visible_chars = 21
    
    if len(current_track) > max_visible_chars:
        scroll_delay += 1
        if scroll_delay >= scroll_speed:
            scroll_delay = 0
            scroll_position += 1
            
            # Reset scroll when we've scrolled past the end
            if scroll_position > len(current_track) - max_visible_chars + 3:
                scroll_position = 0
                time.sleep(1)  # Pause before restarting scroll
            
            # Create scrolled text with padding
            padded_text = current_track + "   "
            display_text = padded_text[scroll_position:scroll_position + max_visible_chars]
            track_label.text = display_text
    else:
        track_label.text = current_track[:max_visible_chars]

def read_serial():
    """Read track info from serial connection"""
    if serial and serial.in_waiting > 0:
        try:
            data = serial.read(serial.in_waiting)
            if data:
                track_info = data.decode('utf-8').strip()
                if track_info:
                    update_track_display(track_info)
                    print(f"Received: {track_info}")
        except Exception as e:
            print(f"Serial error: {e}")

# Main loop
print("Music Pad Ready!")
update_track_display("Waiting for Spotify...")

while True:
    current_time = time.monotonic()
    
    # Read track info from serial
    read_serial()
    
    # Check Switch 1 (Play/Pause)
    if not switch1.value and not switch1_pressed:
        if current_time - last_press_time[0] > debounce_time:
            cc.send(ConsumerControlCode.PLAY_PAUSE)
            print("Play/Pause")
            # Don't override track display, just print
            switch1_pressed = True
            last_press_time[0] = current_time
    elif switch1.value:
        switch1_pressed = False
    
    # Check Switch 2 (Next Track)
    if not switch2.value and not switch2_pressed:
        if current_time - last_press_time[1] > debounce_time:
            cc.send(ConsumerControlCode.SCAN_NEXT_TRACK)
            print("Next Track")
            switch2_pressed = True
            last_press_time[1] = current_time
    elif switch2.value:
        switch2_pressed = False
    
    # Check Switch 3 (Previous Track)
    if not switch3.value and not switch3_pressed:
        if current_time - last_press_time[2] > debounce_time:
            cc.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
            print("Previous Track")
            switch3_pressed = True
            last_press_time[2] = current_time
    elif switch3.value:
        switch3_pressed = False
    
    # Check rotary encoder
    position = encoder.position
    if position != last_position:
        delta = position - last_position
        if delta > 0:
            # Clockwise rotation - Volume Up
            for _ in range(abs(delta)):
                cc.send(ConsumerControlCode.VOLUME_INCREMENT)
            print(f"Volume Up ({delta})")
        else:
            # Counter-clockwise rotation - Volume Down
            for _ in range(abs(delta)):
                cc.send(ConsumerControlCode.VOLUME_DECREMENT)
            print(f"Volume Down ({delta})")
        last_position = position
    
    # Handle text scrolling
    scroll_text()
    
    # Show "No connection" message if no update for 10 seconds
    if current_time - last_track_update > 10 and "Waiting" not in current_track:
        update_track_display("No Spotify connection")
    
    time.sleep(0.01)  # Small delay to prevent CPU overload
