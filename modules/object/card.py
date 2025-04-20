import pygame as pg
from .button import Button
from ..manager import Image_Manager

class Card(Button):
    """卡片物件。繼承自Button。

    由於不同頁面可能需要的卡片功能不同，在創建時呼叫`setClick()`可以自定義。

    Attributes:
        __name (str): 卡片名稱。透過`setName`更改
        __description (str): 卡片描述。透過`setDescription`更改
    
    """
    def __init__(self, pos=(0,0), size:int=50, scale=1, name:str='test_poker'):
        size = (size,size*1.5)
        super().__init__(pos, size, Image_Manager.get(name))
        self.__ori_w = self.width
        self.__ori_h = self.height
        self.width *= scale
        self.height *= scale
        self.__ori_img = self.image
        self.setClick(lambda:print('Clicked Card'))
        self.setWiggle()
        self.__name = "Card"
        self.__description = "This is a description."

    def setName(self, name:str):
        self.__name = name

    def setDescription(self, description:str):
        self.__description = description

    def transform(self, x=None, y=None, scale=None):
        if scale != None:
            self.scale = scale
            self.width = self.__ori_w * scale
            self.height = self.__ori_h * scale
            self.image = pg.transform.smoothscale(self.__ori_img, (self.width, self.height))
            self.rect = self.image.get_rect()
        if x != None:
            self.x = x
        if y != None:
            self.y = y