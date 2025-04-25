import pygame as pg
import os

class Font_Manager:
    """字體管理。

    `get_font`: 取得特定字體大小的Font

    `get_text_surface`: 取得特定文字、大小、顏色的surface

    `draw_text`: 將文字畫在特定surface上
    
    Attributes:
        __font_map (map<tuple(str, int), pg.font.Font>): 此map的鍵為一個tuple,分別為字體名稱以及字體大小,值為對應的Font
        __default_font (str): 預設字體為'Cubic_11'
    """
    __font_map = {}
    __default_font = 'Cubic_11'

    @classmethod
    def get_font(cls, size:int=12) -> pg.font.Font:
        key = size
        if key not in cls.__font_map:
            path = os.path.join('res/font', cls.__default_font + '.ttf')
            cls.__font_map[key] = pg.font.Font(path, size)
        return cls.__font_map[key]
    
    @classmethod
    def get_text_surface(cls, text:str, text_size:int=12, text_color=(255,255,255)) -> pg.surface.Surface:
        font = Font_Manager.get_font(text_size)
        surface = font.render(text, True, text_color)
        return surface

    @classmethod
    def draw_text(cls, surface:pg.Surface, text:str, size:int, x, y, color=(255,255,255)):
        font = cls.get_font(size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x,y))
        surface.blit(text_surface, text_rect)
