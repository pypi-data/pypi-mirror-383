#!/usr/bin/env python3
import pygame
import os

def main():
    try:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)
        pygame.mixer.music.load('./sounds/complete.wav')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.load('./sounds/one_hour.wav')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.load('./sounds/30_minutes.wav')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.load('./sounds/15_minutes.wav')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.load('./sounds/5_minutes.wav')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.load('./sounds/closed.wav')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

    except Exception as e:
        print(f'Error initializing Announcer.\n   {e}')
        raise

if __name__ == "__main__":
    main()
