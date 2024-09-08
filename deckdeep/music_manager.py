import pygame
from pathlib import Path
import random


class BackgroundMusicManager:
    def __init__(self, music_directory: str, volume: float = 0.20):
        self.music_files = [
            str(f)
            for f in Path(music_directory).iterdir()
            if f.suffix in [".mp3", ".ogg", ".wav"]
        ]
        random.shuffle(self.music_files)
        self.current_track_index = 0
        self.volume = max(0.0, min(1.0, volume))

    def __enter__(self):
        if not self.music_files:
            print("No music files found.")
            return self
        pygame.mixer.music.load(self.music_files[self.current_track_index])
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pygame.mixer.music.stop()

    def handle_event(self, event):
        if event.type == pygame.USEREVENT:
            self.current_track_index = random.randint(0, len(self.music_files) - 1)
            pygame.mixer.music.load(self.music_files[self.current_track_index])
            pygame.mixer.music.set_volume(
                self.volume
            )  # Set the volume for the new track
            pygame.mixer.music.play()

    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))  # Ensure volume is between 0.0 and 1.0
        pygame.mixer.music.set_volume(self.volume)
