import os
import pygame as pg

class Image_Manager:
    __img_map = {}

    @classmethod
    def get(cls, key: str):
        if key in cls.__img_map:
            return cls.__img_map[key].copy()

        path = os.path.join('res\\image', key + '.png')
        if not os.path.exists(path):
            raise FileNotFoundError(f"找不到圖片檔案: {path} (key='{key}')")

        img_surface = pg.image.load(path).convert_alpha()
        cls.__img_map[key] = img_surface
        return img_surface.copy()

    @classmethod
    def get_from_path(cls, path: str):
        if path in cls.__img_map:
            return cls.__img_map[path]
        
        if not os.path.exists(path):
            raise FileNotFoundError(f'找不到圖片檔案: {path}')
        img_surface = pg.image.load(path).convert_alpha()
        cls.__img_map[path] = img_surface
        return img_surface