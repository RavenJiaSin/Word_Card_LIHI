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
    def __init__(self, pos:tuple=(0,0), scale:int=1, word:str='apple', font_size:int=30):
        self.__back_img = Image_Manager.get('tmp_card_back').copy()
        self.__front_img = Image_Manager.get('tmp_card_front').copy()
        self.__show_back = True
        self.__word = word
        super().__init__(pos, scale, self.__back_img)

        font = pg.font.Font(font_map['SWEISANSCJKTC-REGULAR'], font_size)
        text_surface = font.render(word, True, (20,20,20))
        text_surface = pg.transform.rotate(text_surface, -90)
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.__front_img.get_size()[0] / 2
        text_rect.centery = self.__front_img.get_size()[1] / 2

        self.__front_img.blit(text_surface, text_rect)
        self.__front_img = pg.transform.rotate(pg.transform.smoothscale(self.__front_img, (self.width, self.height)), 90)

        self.__rotating = True
        self.__rotate_speed = 2
        self.__cache_images = [
            pg.transform.rotate(self.image, angle)
            for angle in range(0, 91, self.__rotate_speed)
        ]
        self.__image_index = -1

        self.setClick(lambda: self.flip())
        self.can_press = False


    # override
    def update(self):
        super().update()
        if self.__rotating:
            self.__image_index += 1
            if self.__image_index == len(self.__cache_images):
                self.__image_index = len(self.__cache_images)-1
                self.__rotating = False
                self.can_press = True
                self.__back_img = pg.transform.rotate(pg.transform.scale(self.__back_img, (self.width, self.height)), 90)
            self.set_ori_image(self.__cache_images[self.__image_index])

    def flip(self):
        if not self.can_press:
            return
        if self.__show_back:
            self.set_ori_image(self.__front_img)
        else:
            self.set_ori_image(self.__back_img)
        self.__show_back = not self.__show_back
        pg.event.post(pg.event.Event(Event_Manager.EVENT_MATCH_CARD_FLIP, {"card":self}))

    def get_word(self):
        return self.__word
    
    def get_show_back(self):
        return self.__show_back