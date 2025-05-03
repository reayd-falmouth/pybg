# check_audio.py
import os
import pygame

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    pygame.mixer.init()
    driver = os.environ.get("SDL_AUDIODRIVER", "(default)")
    print("[✔] pygame.mixer.init() succeeded")
    print("    Requested driver:", driver)
    print("    Mixer init info:", pygame.mixer.get_init())
except pygame.error as e:
    print("[✖] pygame.mixer.init() failed")
    print("    Requested driver:", os.environ.get("SDL_AUDIODRIVER", "(default)"))
    print("    Error:", e)
