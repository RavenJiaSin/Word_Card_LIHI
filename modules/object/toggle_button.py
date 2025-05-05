import pygame as pg
from .button import Button
from ..manager import Image_Manager

class Toggle_Button(Button):
    """切換按鈕物件。繼承自Button。

    可以切換on/off的按鈕，直接拿來用即可，不需要`setClick`
    透過`get()`取得目前狀態

    Attributes:
        __on (bool): 狀態布林值。    
        __off_img (pg.Surface): off的圖片
        __on_img  (pg.Surface): on的圖片
    """
    def __init__(self, pos = (0,0), scale = 1, on_img=None, off_img=None):
        if off_img == None:
            off_img = Image_Manager.get('toggle_button_off')
        if on_img == None:
            on_img = Image_Manager.get('toggle_button_on')
        self.__off_img = pg.transform.smoothscale(off_img, (off_img.get_width()*scale, off_img.get_height()*scale))
        self.__on_img = pg.transform.smoothscale(on_img, (on_img.get_width()*scale, on_img.get_height()*scale))
        super().__init__(pos, 1, self.__on_img)
        self.__on = True
        self.setClick(lambda:self.toggle())
    
    def toggle(self):
        self.__on = not self.__on
        if self.__on:
            self.set_ori_image(self.__on_img)
        else:
            self.set_ori_image(self.__off_img)

    def get(self) -> bool:
        return self.__on