import pygame
from oblique_games import ASSETS_DIR
import time


class SoundManager:
    """Handles game sound effects and background music."""

    def __init__(self):
        pygame.mixer.init()  # Initialize the sound system

        # Load sounds
        self.background_hum = pygame.mixer.Sound(f"{ASSETS_DIR}/audio/hum.ogg")
        self.startup_sound = pygame.mixer.Sound(f"{ASSETS_DIR}/audio/startup.ogg")
        self.button_sound = pygame.mixer.Sound(f"{ASSETS_DIR}/audio/button.ogg")
        self.buzz_sound = pygame.mixer.Sound(f"{ASSETS_DIR}/audio/buzz.ogg")
        self.click_sound = pygame.mixer.Sound(f"{ASSETS_DIR}/audio/click.ogg")
        self.pause_menu_music = pygame.mixer.Sound(f"{ASSETS_DIR}/audio/music.ogg")

        # Set volume levels (Optional: Adjust as needed)
        self.background_hum.set_volume(0.5)
        self.startup_sound.set_volume(1.0)
        self.button_sound.set_volume(1.0)
        self.buzz_sound.set_volume(1.0)
        self.click_sound.set_volume(1.0)
        self.pause_menu_music.set_volume(0.0)  # Start muted
        self.pause_music_active = False  # Flag for tracking pause music state

    def play_background(self):
        """Loops the background sound indefinitely."""
        self.background_hum.play(loops=-1)

    def stop_background(self):
        """Stops the background sound."""
        self.background_hum.stop()

    def play_startup(self):
        """Plays the startup sound once."""
        self.startup_sound.play()

    def play_button_sound(self):
        """Plays the button press sound."""
        self.button_sound.play()

    def play_buzz_sound(self):
        """Plays the buzz press sound."""
        self.buzz_sound.play()

    def play_click_sound(self):
        """Plays the buzz press sound."""
        self.click_sound.play()

    def play_pause_menu_music(self, fade_ms=2000):
        """Starts or resumes the pause menu music."""
        if not self.pause_music_active:
            self.pause_menu_music.play(loops=-1, fade_ms=fade_ms)  # Start playing music
            self.pause_menu_music.set_volume(0.1)  # Set to full volume
            self.pause_music_active = True
        else:
            self.pause_menu_music.set_volume(0.1)  # Just increase volume

    def mute_pause_menu_music(self):
        """Mutes the pause menu music instead of stopping it."""
        self.pause_menu_music.set_volume(0.0)

    def fade_in_music(self, sound, duration=2.0, target_volume=1.0, steps=20):
        """Gradually increases volume of the given sound over time."""
        current_volume = sound.get_volume()
        step_size = (target_volume - current_volume) / steps
        step_delay = duration / steps

        for _ in range(steps):
            current_volume += step_size
            sound.set_volume(
                max(0.0, min(target_volume, current_volume))
            )  # Clamp between 0 and target
            time.sleep(step_delay)  # Pause to create fade-in effect
