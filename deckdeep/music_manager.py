import pygame
from pathlib import Path

class BackgroundMusicManager:
    def __init__(self, music_directory: str):
        self.music_files = [str(f) for f in Path(music_directory).iterdir() if f.suffix in ['.mp3', '.ogg', '.wav']]
        self.current_track_index = 0

    def __enter__(self):
        if not self.music_files:
            print("No music files found.")
            return self

        pygame.mixer.music.load(self.music_files[self.current_track_index])
        pygame.mixer.music.play()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pygame.mixer.music.stop()

    def handle_event(self, event):
        if event.type == pygame.USEREVENT:
            self.current_track_index = (self.current_track_index + 1) % len(self.music_files)
            pygame.mixer.music.load(self.music_files[self.current_track_index])
            pygame.mixer.music.play()