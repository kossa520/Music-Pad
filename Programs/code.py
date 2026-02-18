import board
import busio
import digitalio
import usb_hid
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
import time
import adafruit_ssd1306
import usb_cdc

# Initialize I2C for OLED
i2c = busio.I2C(board.SCL, board.SDA)

# Create the SSD1306 OLED display (128x32 pixels, I2C address 0x3C)
WIDTH = 128
HEIGHT = 32
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C)

# Rotate display 180 degrees (upside down fix)
oled.rotation = 2

# Initialize USB HID devices
cc = ConsumerControl(usb_hid.devices)
kbd = Keyboard(usb_hid.devices)
mouse = Mouse(usb_hid.devices)

# Initialize USB Serial
serial = usb_cdc.data

# Configure GPIO pins for switches
switch1_pin = board.D0  # GPIO26 - Play/Pause
switch2_pin = board.D1  # GPIO27 - Previous Track
switch3_pin = board.D2  # GPIO28 - Next Track

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

# Setup rotary encoder with manual reading
encoder_a = digitalio.DigitalInOut(board.D3)  # GPIO29
encoder_a.direction = digitalio.Direction.INPUT
encoder_a.pull = digitalio.Pull.UP

encoder_b = digitalio.DigitalInOut(board.D7)  # GPIO1/RX
encoder_b.direction = digitalio.Direction.INPUT
encoder_b.pull = digitalio.Pull.UP

# Setup encoder button
encoder_btn_pin = board.D6  # GPIO0 - Encoder button
encoder_btn = digitalio.DigitalInOut(encoder_btn_pin)
encoder_btn.direction = digitalio.Direction.INPUT
encoder_btn.pull = digitalio.Pull.UP

# Mode tracking: 0 = Music mode, 1 = Arrow/Mouse mode
mode = 0
mode_names = ["Music", "Arrow"]

# Encoder state tracking
last_a = encoder_a.value
last_b = encoder_b.value
encoder_position = 0
encoder_state = 0
last_encoder_time = 0
encoder_debounce = 0.01

def read_encoder():
    global last_a, last_b, encoder_position, encoder_state, last_encoder_time

    current_time = time.monotonic()

    if current_time - last_encoder_time < encoder_debounce:
        return encoder_position

    a = encoder_a.value
    b = encoder_b.value

    if a == last_a and b == last_b:
        return encoder_position

    last_encoder_time = current_time

    current_state = (a << 1) | b
    combined = (encoder_state << 2) | current_state

    if combined == 0b0010 or combined == 0b1011 or combined == 0b1101 or combined == 0b0100:
        encoder_position += 1
    elif combined == 0b0001 or combined == 0b0111 or combined == 0b1110 or combined == 0b1000:
        encoder_position -= 1

    encoder_state = current_state
    last_a = a
    last_b = b

    return encoder_position

def send_volume_up():
    cc.send(ConsumerControlCode.VOLUME_INCREMENT)

def send_volume_down():
    cc.send(ConsumerControlCode.VOLUME_DECREMENT)

# Variables for switch debouncing
switch1_pressed = False
switch2_pressed = False
switch3_pressed = False
encoder_btn_pressed = False
debounce_time = 0.2
last_press_time = [0, 0, 0, 0]

# Variable for encoder position
last_position = 0

# Display variables
current_track = "Loading..."
scroll_position = 0
scroll_delay = 0
scroll_speed = 3
last_track_update = time.monotonic()
display_update_counter = 0

# Serial buffer for newline-terminated messages
serial_buffer = ""

def draw_simple_text(text, start_col=0, start_row=0):
    font = {
        ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
        '!': [0x00, 0x00, 0x5F, 0x00, 0x00],
        '"': [0x00, 0x07, 0x00, 0x07, 0x00],
        '#': [0x14, 0x7F, 0x14, 0x7F, 0x14],
        '$': [0x24, 0x2A, 0x7F, 0x2A, 0x12],
        '%': [0x23, 0x13, 0x08, 0x64, 0x62],
        '&': [0x36, 0x49, 0x55, 0x22, 0x50],
        "'": [0x00, 0x05, 0x03, 0x00, 0x00],
        '(': [0x00, 0x1C, 0x22, 0x41, 0x00],
        ')': [0x00, 0x41, 0x22, 0x1C, 0x00],
        '*': [0x14, 0x08, 0x3E, 0x08, 0x14],
        '+': [0x08, 0x08, 0x3E, 0x08, 0x08],
        ',': [0x00, 0x50, 0x30, 0x00, 0x00],
        '-': [0x08, 0x08, 0x08, 0x08, 0x08],
        '.': [0x00, 0x60, 0x60, 0x00, 0x00],
        '/': [0x20, 0x10, 0x08, 0x04, 0x02],
        '0': [0x3E, 0x51, 0x49, 0x45, 0x3E],
        '1': [0x00, 0x42, 0x7F, 0x40, 0x00],
        '2': [0x42, 0x61, 0x51, 0x49, 0x46],
        '3': [0x21, 0x41, 0x45, 0x4B, 0x31],
        '4': [0x18, 0x14, 0x12, 0x7F, 0x10],
        '5': [0x27, 0x45, 0x45, 0x45, 0x39],
        '6': [0x3C, 0x4A, 0x49, 0x49, 0x30],
        '7': [0x01, 0x71, 0x09, 0x05, 0x03],
        '8': [0x36, 0x49, 0x49, 0x49, 0x36],
        '9': [0x06, 0x49, 0x49, 0x29, 0x1E],
        ':': [0x00, 0x36, 0x36, 0x00, 0x00],
        'A': [0x7E, 0x09, 0x09, 0x09, 0x7E],
        'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
        'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
        'D': [0x7F, 0x41, 0x41, 0x22, 0x1C],
        'E': [0x7F, 0x49, 0x49, 0x49, 0x41],
        'F': [0x7F, 0x09, 0x09, 0x09, 0x01],
        'G': [0x3E, 0x41, 0x49, 0x49, 0x7A],
        'H': [0x7F, 0x08, 0x08, 0x08, 0x7F],
        'I': [0x00, 0x41, 0x7F, 0x41, 0x00],
        'J': [0x20, 0x40, 0x41, 0x3F, 0x01],
        'K': [0x7F, 0x08, 0x14, 0x22, 0x41],
        'L': [0x7F, 0x40, 0x40, 0x40, 0x40],
        'M': [0x7F, 0x02, 0x0C, 0x02, 0x7F],
        'N': [0x7F, 0x04, 0x08, 0x10, 0x7F],
        'O': [0x3E, 0x41, 0x41, 0x41, 0x3E],
        'P': [0x7F, 0x09, 0x09, 0x09, 0x06],
        'Q': [0x3E, 0x41, 0x51, 0x21, 0x5E],
        'R': [0x7F, 0x09, 0x19, 0x29, 0x46],
        'S': [0x46, 0x49, 0x49, 0x49, 0x31],
        'T': [0x01, 0x01, 0x7F, 0x01, 0x01],
        'U': [0x3F, 0x40, 0x40, 0x40, 0x3F],
        'V': [0x1F, 0x20, 0x40, 0x20, 0x1F],
        'W': [0x7F, 0x20, 0x18, 0x20, 0x7F],
        'X': [0x41, 0x22, 0x1C, 0x22, 0x41],
        'Y': [0x07, 0x08, 0x70, 0x08, 0x07],
        'Z': [0x61, 0x51, 0x49, 0x45, 0x43],
        'a': [0x20, 0x54, 0x54, 0x54, 0x78],
        'b': [0x7F, 0x48, 0x44, 0x44, 0x38],
        'c': [0x38, 0x44, 0x44, 0x44, 0x20],
        'd': [0x38, 0x44, 0x44, 0x48, 0x7F],
        'e': [0x38, 0x54, 0x54, 0x54, 0x18],
        'f': [0x08, 0x7E, 0x09, 0x01, 0x02],
        'g': [0x0C, 0x52, 0x52, 0x52, 0x3E],
        'h': [0x7F, 0x08, 0x04, 0x04, 0x78],
        'i': [0x00, 0x44, 0x7D, 0x40, 0x00],
        'j': [0x20, 0x40, 0x44, 0x3D, 0x00],
        'k': [0x7F, 0x10, 0x28, 0x44, 0x00],
        'l': [0x00, 0x41, 0x7F, 0x40, 0x00],
        'm': [0x7C, 0x04, 0x18, 0x04, 0x78],
        'n': [0x7C, 0x08, 0x04, 0x04, 0x78],
        'o': [0x38, 0x44, 0x44, 0x44, 0x38],
        'p': [0x7C, 0x14, 0x14, 0x14, 0x08],
        'q': [0x08, 0x14, 0x14, 0x18, 0x7C],
        'r': [0x7C, 0x08, 0x04, 0x04, 0x08],
        's': [0x48, 0x54, 0x54, 0x54, 0x20],
        't': [0x04, 0x3F, 0x44, 0x40, 0x20],
        'u': [0x3C, 0x40, 0x40, 0x20, 0x7C],
        'v': [0x1C, 0x20, 0x40, 0x20, 0x1C],
        'w': [0x3C, 0x40, 0x30, 0x40, 0x3C],
        'x': [0x44, 0x28, 0x10, 0x28, 0x44],
        'y': [0x1C, 0x20, 0x40, 0x20, 0x1C],
        'z': [0x44, 0x64, 0x54, 0x4C, 0x44],
    }

    x = start_col
    for char in text:
        if x >= WIDTH - 6:
            break

        if char in font:
            pattern = font[char]
            for col_idx, col_data in enumerate(pattern):
                for row in range(8):
                    if col_data & (1 << row):
                        oled.pixel(x + col_idx, start_row + row, 1)
        x += 6  # Always advance, skips unknown chars cleanly

def update_display_simple():
    global scroll_position, scroll_delay, display_update_counter

    display_update_counter += 1
    if display_update_counter < 10:
        return
    display_update_counter = 0

    oled.fill(0)

    if mode == 0:
        draw_simple_text("Music", 0, 0)
    else:
        draw_simple_text("Arrow", 0, 0)

    # Infinite scrolling - text loops continuously without going back
    scroll_delay += 1
    if scroll_delay >= scroll_speed:
        scroll_delay = 0
        scroll_position += 1
        # Reset when we've scrolled through the whole text + gap
        if scroll_position >= len(current_track) + 5:
            scroll_position = 0

    # Build looping text: "song name     song name     ..."
    looping_text = current_track + "     " + current_track + "     "
    visible_text = looping_text[scroll_position:scroll_position + 20]
    draw_simple_text(visible_text, 0, 18)

    oled.show()

def update_track_display(text):
    global current_track, scroll_position, last_track_update
    if text != current_track:
        current_track = text
        scroll_position = 0
        last_track_update = time.monotonic()

def read_serial():
    """Read track info from serial - newline terminated"""
    global serial_buffer, last_track_update
    if serial and serial.in_waiting > 0:
        try:
            data = serial.read(serial.in_waiting)
            if data:
                serial_buffer += data.decode('utf-8')
                while '\n' in serial_buffer:
                    line, serial_buffer = serial_buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        last_track_update = time.monotonic()  # always reset timer
                        update_track_display(line)
                        print(f"Received: {line}")
        except Exception as e:
            print(f"Serial error: {e}")

# Initialize display
oled.fill(0)
oled.show()
update_display_simple()

print("Music Pad Ready!")
print("Mode: Music")

while True:
    current_time = time.monotonic()

    read_serial()

    # Check encoder button for mode switching
    if not encoder_btn.value and not encoder_btn_pressed:
        if current_time - last_press_time[3] > debounce_time:
            mode = 1 - mode

            if mode == 0:
                kbd.send(Keycode.ENTER)
                print("Enter pressed")

            print(f"Mode switched to: {mode_names[mode]}")
            update_track_display(f"Mode: {mode_names[mode]}")
            encoder_btn_pressed = True
            last_press_time[3] = current_time
    elif encoder_btn.value:
        encoder_btn_pressed = False

    # Check Switch 1 (Play/Pause)
    if not switch1.value and not switch1_pressed:
        if current_time - last_press_time[0] > debounce_time:
            cc.send(ConsumerControlCode.PLAY_PAUSE)
            print("Play/Pause")
            switch1_pressed = True
            last_press_time[0] = current_time
    elif switch1.value:
        switch1_pressed = False

    # Check Switch 2 (Previous Track)
    if not switch2.value and not switch2_pressed:
        if current_time - last_press_time[1] > debounce_time:
            cc.send(ConsumerControlCode.SCAN_PREVIOUS_TRACK)
            print("Previous Track")
            switch2_pressed = True
            last_press_time[1] = current_time
    elif switch2.value:
        switch2_pressed = False

    # Check Switch 3 (Next Track)
    if not switch3.value and not switch3_pressed:
        if current_time - last_press_time[2] > debounce_time:
            cc.send(ConsumerControlCode.SCAN_NEXT_TRACK)
            print("Next Track")
            switch3_pressed = True
            last_press_time[2] = current_time
    elif switch3.value:
        switch3_pressed = False

    # Check rotary encoder
    position = read_encoder()
    if position != last_position:
        delta = position - last_position
        if abs(delta) >= 2:
            steps = delta // 2
            if mode == 0:  # Music mode
                if steps > 0:
                    for _ in range(abs(steps)):
                        kbd.send(Keycode.SHIFT, Keycode.F22)
                    print(f"Shift + F22 ({steps})")
                elif steps < 0:
                    for _ in range(abs(steps)):
                        kbd.send(Keycode.SHIFT, Keycode.F23)
                    print(f"Shift + F23 ({abs(steps)})")
            else:  # Arrow mode
                if steps > 0:
                    for _ in range(abs(steps)):
                        kbd.send(Keycode.DOWN_ARROW)
                    print(f"Down Arrow ({steps})")
                elif steps < 0:
                    for _ in range(abs(steps)):
                        kbd.send(Keycode.UP_ARROW)
                    print(f"Up Arrow ({abs(steps)})")
            last_position = position

    update_display_simple()

    if current_time - last_track_update > 10 and "Waiting" not in current_track and "Mode" not in current_track:
        update_track_display("No connection")

    time.sleep(0.005)
