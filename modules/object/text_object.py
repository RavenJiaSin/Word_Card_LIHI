import pygame as pg
from .object import Object
from modules.manager import Font_Manager

class Text_Object(Object):
    def __init__(self, pos:tuple=(0,0), text='text', font_size=60, font_color = (230,230,230),):
        font = Font_Manager.get_font(font_size)
        text_surface = font.render(text, True, font_color)
        super().__init__(pos=pos, scale=1, img=text_surface)