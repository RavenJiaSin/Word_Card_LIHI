import pygame as pg
from .button import Button
from ..manager import Image_Manager
from ..manager import Font_Manager

class Toggle_Button(Button):
    """切換按鈕物件。繼承自Button。

    可以切換on/off的按鈕，直接拿來用即可，不需要`setClick`
    透過`get()`取得目前狀態

    Attributes:
        __on (bool): 狀態布林值。    
        __off_img (pg.Surface): off的圖片
        __on_img  (pg.Surface): on的圖片
    """
    def __init__(self, pos = (0,0), scale = 1, label = '', on_img=None, off_img=None):
        if off_img == None:
            off_img = Image_Manager.get('toggle_button_off')
        if on_img == None:
            on_img = Image_Manager.get('toggle_button_on')

        off_img = self.image_add_label(off_img, label)
        on_img = self.image_add_label(on_img, label)

        self.__off_img = pg.transform.smoothscale(off_img, (off_img.get_width()*scale, off_img.get_height()*scale))
        self.__on_img = pg.transform.smoothscale(on_img, (on_img.get_width()*scale, on_img.get_height()*scale))
        super().__init__(pos, 1, self.__on_img)
        self.__on = True
        self.__label = label
        self.setClick(lambda:self.toggle())
    
    def image_add_label(self, img:pg.Surface, label:str, padding:int=10) -> pg.Surface:    
        img_width, img_height = img.get_size()
        label_surf = Font_Manager.get_text_surface(label, 96)
        label_width, label_height = label_surf.get_size()

        total_width = max(img_width, label_width)
        total_height = img_height + padding + label_height

        # 新 surface
        img_with_label = pg.Surface((total_width, total_height), pg.SRCALPHA)

        # 計算置中位置
        img_x = (total_width - img_width) // 2
        label_x = (total_width - label_width) // 2
        label_y = img_height + padding

        # blit 圖片和文字
        img_with_label.blit(img, (img_x, 0))
        img_with_label.blit(label_surf, (label_x, label_y))

        return img_with_label

    def toggle(self):
        self.__on = not self.__on
        if self.__on:
            self.set_ori_image(self.__on_img)
        else:
            self.set_ori_image(self.__off_img)

    def get_state(self) -> bool:
        return self.__on

    def get_label(self) -> str:
        return self.__label