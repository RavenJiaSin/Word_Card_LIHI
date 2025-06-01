import pygame as pg
import game
from .button import Button
from .object import Object
from ..manager import Event_Manager
from ..manager import Image_Manager
from ..manager import SFX_Manager

class Text_Sound_Button(Button):
    def __init__(self, pos = (0,0), scale = 1, text = str):
        super().__init__(pos, scale, Image_Manager.get('sound'), sound=text)