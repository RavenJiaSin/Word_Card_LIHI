import pygame as pg
from .button import Button
import game
from modules.manager import Font_Manager

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
    def __init__(self, pos:tuple=(0,0), img=None, text='text', font_color = (20,20,20), font_size=60):
        super().__init__(pos=pos, scale=1, img=img)
                
        font = Font_Manager.get_font(font_size)
        text_surface = font.render(text, True, font_color)
        self.set_ori_image(pg.transform.scale(self.image, (text_surface.get_width()+40,self.height)))
        text_rect = text_surface.get_rect(center=(self.width / 2,self.height / 2))
        self.image.blit(text_surface, text_rect)