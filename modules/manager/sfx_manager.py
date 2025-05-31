import pygame
import os

class SFX_Manager:
    _sounds = {}

    @classmethod
    def init(cls):
        pygame.mixer.init()
        for filename in os.listdir('res/sfx'):
            if filename.lower().endswith((".wav", ".ogg")):
                name = os.path.splitext(filename)[0]  # 檔名去掉副檔名
                path = os.path.join('res/sfx', filename)
                cls._sounds[name] = pygame.mixer.Sound(path)

    @classmethod
    def play(cls, name, loops=0):
        if name in cls._sounds:
            cls._sounds[name].play(loops=loops)
        else:
            print(f"[SFX_Manager] 音效 '{name}' 未載入。")

    @classmethod
    def set_volume(cls, name, volume):
        if name in cls._sounds:
            cls._sounds[name].set_volume(volume)

    @classmethod
    def stop(cls, name):
        if name in cls._sounds:
            cls._sounds[name].stop()

    @classmethod
    def stop_all(cls):
        pygame.mixer.stop()
