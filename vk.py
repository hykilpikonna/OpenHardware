import ctypes
from ctypes import wintypes

# Virtual-Key codes
# RESERVED: 0xEA
VK = 0x6B
KEYEVENTF_KEYUP = 0x0002

def press_key(vk_code = VK):
    scan_code = ctypes.windll.user32.MapVirtualKeyA(vk_code, 0)
    ctypes.windll.user32.keybd_event(vk_code, scan_code, 0, 0)

def release_key(vk_code = VK):
    scan_code = ctypes.windll.user32.MapVirtualKeyA(vk_code, 0)
    ctypes.windll.user32.keybd_event(vk_code, scan_code, KEYEVENTF_KEYUP, 0)