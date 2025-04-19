import pygame as pg
from .button import Button
import game
from modules.manager import font_map

class Text_Button(Button):
    """文字按鈕物件。繼承自Button。

    可以判斷是否被點擊。繼承時 *不建議覆寫* `_handle_event()` 以及 `setClick()`。

    繼承範例參考 `Card`。

    Attributes:
        __click (function): 描述點擊按鈕後要發生什麼事。
        __wiggle (bool): 是否抖動。
        __ori_y (float): 紀錄初始y位置。
        __goDown (bool): 紀錄抖動正在下降還是上升
    """
    def __init__(self, pos:tuple=(0,0), size:tuple=(32,32), img=None, text='text', font='SWEISANSCJKTC-REGULAR', font_size=16, font_color = (200,200,200)):
        super().__init__(pos=pos, size=size, img=img)
        self.__text = text
        self.__font = font
        self.__font_size = font_size
        
        font = pg.font.Font(font_map[font], font_size)
        text_surface = font.render(text, True, font_color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = self.width / 2
        text_rect.centery = self.height / 2
        self.image.blit(text_surface, text_rect)
        