import os
from pathlib import Path
import time
import serial
import re
from vk import *
import winsound

# Configure your serial port and baud rate
SERIAL_PORT = 'COM3'  # Replace 'COMx' with your serial port (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux)
# SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
PATH = Path('C:/MUGS/felica.txt')
# PATH = Path('/tmp/felica.txt')

AUDIO_EFFECT = Path(__file__).parent / 'Audio/mixkit-gaming-lock-2848.wav'

def parse_uid(data):
    """
    Parse the UID from the serial data.
    """
    uid_value_match = re.search(r'UID Value: ([0-9A-F]+)', data)

    if uid_value_match:
        uid = uid_value_match.group(1)
        
        # If UID is not 8 bytes, pad it with zeros
        if len(uid) < 16:
            uid = uid.zfill(16)
        
        # If the UID Doesn't start with 01 2E, set it to 01 2E
        if uid[:4] != '012E':
            uid = '012E' + uid[4:]
        
        # Write the UID to the file
        print(f"UID: {uid}")
        PATH.write_text(uid)
        
        # Play audio effect
        winsound.PlaySound(str(AUDIO_EFFECT), winsound.SND_FILENAME)
        
        # Press scan button
        for i in range(3):
            press_key()
            time.sleep(0.1)
            release_key()
            time.sleep(0.1)
        
        return uid
    

if __name__ == "__main__":
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Listening on {SERIAL_PORT}...")

    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                print(line)
                parse_uid(line)
                    
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()