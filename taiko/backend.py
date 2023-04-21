"""
This script reads the Arduino's serial output and convert it to keyboard input.

Requirements: pip install pyserial keyboard matplotlib
"""
import time

import keyboard
import serial.tools.list_ports

TAIKO_KEYS = ['f', 'd']


if __name__ == '__main__':
    # List serial ports
    ports = serial.tools.list_ports.comports()

    # If there are no ports, exit
    if not ports:
        print('No serial ports found!')
        exit(1)

    # If there are more than one serial port, print them out
    if len(ports) > 1:
        print('Multiple serial ports found:')
        for i, port in enumerate(ports):
            print(f'[{i}] {port.device}')
        print()

        # Ask the user to select one
        inp = input('Select a port: ')
        port = ports[int(inp)].device

    # If there is only one serial port, use it
    else:
        port = ports[0].device

    # Open the serial port
    print(f'Opening serial port {port}...')
    ser = serial.Serial(port, 115200)

    # Read the serial port
    try:
        start_time = time.time()
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print(line)

            # If the line starts with ";", it's a plot point
            if line.startswith(';'):
                line = line[1:].split(';')
                ys = [float(y) / 1024.0 for y in line]
                yleft, yright = ys

            # If the line starts with ":", it's a keyboard input
            elif line.startswith('Hit:'):
                # Index of the drumstick that hit the piezo
                line = line[4:]
                cmd = line[0]
                key = TAIKO_KEYS[int(line[1:])]

                if cmd == "+":
                    keyboard.press(key)
                elif cmd == "-":
                    keyboard.release(key)

    except KeyboardInterrupt:
        ser.close()
        print('Closed serial port.')
