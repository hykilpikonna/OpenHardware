# Requirements: pyserial, hypy_utils, pygame
import ctypes
import math
import os
import threading
from typing import NamedTuple, Literal

import pygame
import serial
from hypy_utils.logging_utils import setup_logger

log = setup_logger()


class TouchArea(NamedTuple):
    category: Literal['A', 'B', 'C', 'D', 'E']
    index: int

    def __str__(self):
        return self.category + str(self.index)


touch_areas = (
        [TouchArea('A', i + 1) for i in range(8)] +
        [TouchArea('B', i + 1) for i in range(8)] +
        [TouchArea('C', i + 1) for i in range(2)] +
        [TouchArea('D', i + 1) for i in range(8)] +
        [TouchArea('E', i + 1) for i in range(8)]
)


def convert(d: str) -> list[TouchArea]:
    """
    Convert maimai touch data string into touch areas activated.

    The maimai touch data is a letter representation of bitwise data.

    When nothing is touched, d = "@@@@@@@"
    When A1 is touched, d = "A@@@@@@"
    When A2 is touched, d = "B@@@@@@"
    When A3 is touched, d = "D@@@@@@"
    When both A1 and A2 are touched, d = "C@@@@@@" (A + B = C)
    When both A1 and A3 are touched, d = "E@@@@@@" (A + D = E)
    When all three are touched, d = "G@@@@@@" (A + B + D = G)

    Raw letter orders are A (1) B (10) D (100) H (1000) P (10000)

    :param d: Maimai touch data (single frame)
    :return: List of touch areas activated
    """
    # Loop through each digit
    for ci, c in enumerate(d):
        if c == "@":
            continue

        # Convert it to ordinal number (A = 1)
        # The binary of oi will show 5 bits, each representing if the touch area is activated.
        oi = ord(c) - ord('A') + 1

        # Find bits activated
        for i in range(5):
            if oi & (1 << i):
                yield touch_areas[ci * 5 + i]


def serial_listen(callback: callable, port: str = 'COM3'):
    """
    Listen for serial data from mai touch device.

    Official port: COM3
    Baud rate: 9600
    Frame format: (@@@@@@@)

    :param callback: Callback function when touch data is received
    :param port: Serial port to listen to
    """
    # Open serial
    ser = serial.Serial(port, 9600)

    # Align frame
    while ser.read(1).decode('utf-8') != ')':
        pass

    # Loop forever
    frame = ''
    while True:
        # Read a frame
        frame += ser.read(9).decode('utf-8')
        log.debug(f"Received frame: {frame}")

        assert frame[0] == '('
        assert frame[-1] == ')'
        assert len(frame) == 9

        # Parse
        ta = list(convert(frame[1:-1]))
        frame = ''

        # Callback
        callback(ta)


def serial_listen_btn(callback: callable, port: str = 'COM25'):
    """
    Listen for serial data from mai_pico io4 buttons.

    Frame format: BTN 000000000000;\n

    :param callback: Callback function when button state changes
    :param port: Serial port to listen to
    """
    # Open serial
    ser = serial.Serial(port, 9600)

    # Loop forever
    while True:
        ser.read_until(b'BTN ')
        frame = ser.read_until(b';').decode('utf-8')
        log.debug(f"Received frame: {frame}")

        # Callback
        callback(frame.strip(';'))


def test_callback(ta: list[TouchArea]):
    log.info(f"Received touch areas: {' '.join(map(str, ta))}")


def test_callback_btn(btn: str):
    log.info(f"Received button state: {btn}")


# Configuration: VK codes for DFJK
TAIKO_KEYS = [0x44, 0x46, 0x4A, 0x4B]
SCAN_CODES = [ctypes.windll.user32.MapVirtualKeyA(k, 0) for k in TAIKO_KEYS]

# State and macros
TAIKO_STATES = [False] * len(TAIKO_KEYS)
TAIKO_LEFT_KA = 0
TAIKO_LEFT_DON = 1
TAIKO_RIGHT_DON = 2
TAIKO_RIGHT_KA = 3


def taiko_callback(ta: list[TouchArea]):
    """
    Convert mai touch to taiko keyboard input

    D1, D5, E1, E5 are ignored (they're located in the center

    A1-4, B1-4, D2-4, E2-4, C1 are right Don
    Others are left Don
    """
    states = [False] * len(TAIKO_KEYS)
    for t in ta:
        if str(t) in ('D1', 'D5', 'E1', 'E5'):
            continue
        if (t.category in 'ABDE' and t.index in (1, 2, 3, 4)) or \
           (t.category == 'C' and t.index == 1):
            states[TAIKO_RIGHT_DON] = True
        else:
            states[TAIKO_LEFT_DON] = True
    taiko_after_update(states)


def taiko_after_update(states: list[bool], is_btn: bool = False):
    # Check state changes
    for i, (old, new) in enumerate(zip(TAIKO_STATES, states)):
        if ((is_btn and i in (TAIKO_LEFT_DON, TAIKO_RIGHT_DON)) or
           (not is_btn and i in (TAIKO_LEFT_KA, TAIKO_RIGHT_KA))):
            continue
        if old == new:
            continue

        TAIKO_STATES[i] = new
        # Send key up/down
        ctypes.windll.user32.keybd_event(TAIKO_KEYS[i], SCAN_CODES[i], 0 if new else 2, 0)


def taiko_callback_btn(btn: str):
    """
    Convert mai_pico io4 buttons to taiko keyboard input

    Button index 0-3 are right Ka, 4-7 are left Ka
    """
    print(btn)
    states = [False] * len(TAIKO_KEYS)
    states[TAIKO_RIGHT_KA] = '1' in btn[0:4]
    states[TAIKO_LEFT_KA] = '1' in btn[4:8]
    taiko_after_update(states, True)


def start_serial_threads():
    thread1 = threading.Thread(target=serial_listen, args=(taiko_callback, 'COM3'))
    thread2 = threading.Thread(target=serial_listen_btn, args=(taiko_callback_btn, 'COM25'))
    thread1.start()
    thread2.start()


if __name__ == '__main__':
    # Default window location at bottom
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'0,{1920-1080}'

    # Start pygame window
    pygame.init()
    W = 1080
    CW = 0.8
    pygame.display.set_mode((W, W))
    pygame.display.set_caption("MaiTouch")

    # Start serial threads
    start_serial_threads()

    COLOR_DON_OFF = '#fc9f9f'
    COLOR_DON_ON = '#ff4242'
    COLOR_KA_OFF = '#9fe3fc'
    COLOR_KA_ON = '#0f68f7'
    DELTA_DEG = 0.1

    def color(idx):
        if idx in (TAIKO_LEFT_KA, TAIKO_RIGHT_KA):
            return COLOR_KA_ON if TAIKO_STATES[idx] else COLOR_KA_OFF
        return COLOR_DON_ON if TAIKO_STATES[idx] else COLOR_DON_OFF

    # Game loop
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    os._exit(0)

            # White background
            pygame.display.get_surface().fill((255, 255, 255))
            # Taiko Don (two red half-circles in the center)
            mar = (W * (1 - CW)) / 2
            pygame.draw.arc(pygame.display.get_surface(), color(TAIKO_LEFT_DON), (mar, mar, W * CW, W * CW), math.pi / 2, - math.pi / 2, 5000)
            pygame.draw.arc(pygame.display.get_surface(), color(TAIKO_RIGHT_DON), (mar, mar, W * CW, W * CW), - math.pi / 2, math.pi / 2, 5000)
            # Taiko Ka (two blue arches (empty half-circles) on the sides)
            pygame.draw.arc(pygame.display.get_surface(), color(TAIKO_LEFT_KA), (0, 0, W, W), math.pi / 2, - math.pi / 2, 80)
            pygame.draw.arc(pygame.display.get_surface(), color(TAIKO_RIGHT_KA), (0, 0, W, W), - math.pi / 2, math.pi / 2, 80)
            # Thin rectangle dividing the middle
            rw = 20
            pygame.draw.rect(pygame.display.get_surface(), '#FFFFFF', (W / 2 - rw / 2, 0, rw, W))
            pygame.display.flip()

    except KeyboardInterrupt:
        os._exit(0)
