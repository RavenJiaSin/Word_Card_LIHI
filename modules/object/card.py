import pygame as pg
from .button import Button
from ..manager import Image_Manager
from ..manager import font_map

class Card(Button):
    """卡片物件。繼承自Button。

    由於不同頁面可能需要的卡片功能不同，在創建時呼叫`setClick()`可以自定義。

    Attributes:
        __id (str): 卡片名稱。    
    """
    def __init__(self, pos=(0,0), size:int=50, id:str='Card'):
        self.__id = id
        size = (size,size*1.5)
        super().__init__(pos, size, Image_Manager.get('tmp_card_front'))
        self.__set_image()
        self.setClick(lambda:print('Clicked Card:', self.__id))

    def __set_image(self):
        font = pg.font.Font(font_map['test_font'], 20)
        text_surface = font.render(self.__id, True, (0,0,0))
        text_rect = text_surface.get_rect()

        text_rect.centerx = self.width / 2
        text_rect.centery = self.height / 2

        self.image.blit(text_surface, text_rect)