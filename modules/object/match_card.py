import pygame as pg
from .button import Button
from ..manager import Image_Manager
from ..manager import font_map
from ..manager import Event_Manager


class Match_Card(Button):
    """配對遊戲卡片物件。繼承自Button。

    用於配對小遊戲的卡片物件

    Attributes:
        __back_img (Surface): 卡片背面。
        __front_img (Surface): 卡片正面，有單字。
        __show_back (Bool): 是否正在顯示卡片背面。
        __word (str): 卡片正面的單字
    """
    def __init__(self, pos:tuple=(0,0), size:int=50, word:str='apple', font_size:int=30):
        size = (size,size*1.5)
        self.__back_img = Image_Manager.get('tmp_card_back').copy()
        self.__front_img = Image_Manager.get('tmp_card_front').copy()
        self.__show_back = True
        self.__word = word
        super().__init__(pos, size, self.__back_img)

        font = pg.font.Font(font_map['SWEISANSCJKTC-REGULAR'], font_size)
        text_surface = font.render(word, True, (20,20,20))
        text_surface = pg.transform.rotate(text_surface, -90)
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.__front_img.get_size()[0] / 2
        text_rect.centery = self.__front_img.get_size()[1] / 2

        self.__front_img.blit(text_surface, text_rect)

        self.__angle = 0
        self.__rotate_speed = 2

        self.setClick(lambda: self.flip())
        self.can_flip = True


    # override
    def update(self):
        super().update()
        self.__angle += self.__rotate_speed
        if self.__angle > 90:
            self.__angle = 90
        self.image = pg.transform.rotate(self.image, self.__angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def flip(self):
        if not self.can_flip:
            return
        if self.__show_back:
            self.image = pg.transform.scale(self.__front_img, (self.width, self.height))
            self.ori_image = self.image
        else:
            self.image = pg.transform.scale(self.__back_img, (self.width, self.height))
            self.ori_image = self.image
        self.__show_back = not self.__show_back
        pg.event.post(pg.event.Event(Event_Manager.EVENT_MATCH_CARD_FLIP, {"card":self}))

    def get_word(self):
        return self.__word
    
    def get_show_back(self):
        return self.__show_back