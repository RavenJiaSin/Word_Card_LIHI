from typing import Callable
import pygame as pg
import game
from .object import Object
from ..manager import Image_Manager
from ..manager import Event_Manager

class Button(Object):
    """按鈕物件。繼承自Object。

    可以判斷是否被點擊。繼承時 *不建議覆寫* `_handle_event()` 以及 `setClick()`。

    繼承範例參考 `Card`。

    Attributes:
        __click (function): 描述點擊按鈕後要發生什麼事。
        __wiggle (bool): 是否抖動。
        __ori_y (float): 紀錄初始y位置。
        __goDown (bool): 紀錄抖動正在下降還是上升
    """
    def __init__(self, pos:tuple=(0,0), scale:float=1, img=None):
        if img == None:
            img = Image_Manager.get('button')
        super().__init__(pos=pos, scale=scale, img=img)
        self.__click = lambda:None
        self.__isPressed = False

        self.scale_for_transform = 1                    # 當前縮放倍率
        self.__ori_w = self.width
        self.__ori_h = self.height

        self.__ori_image = self.image
        self.ori_scale = self.scale_for_transform       # Card會用到，不加底線
        self.__delta_press_scale = 0.1                  # 點擊時的縮放倍率變化量
        self.__press_scale_speed = 0.45                 # 點擊時每幀縮放變化的速度

        self.can_press = True
        self.is_hover = False
        self.mouse_enter = False
        self.mouse_exit = False

    # override
    def handle_event(self):
        event_list = game.event_list.copy()  # 避免因 remove 導致迭代出錯
        for e in event_list:
            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1 and self.can_press:
                mx, my = e.pos
                scaled_pos = (mx * game.MOUSE_SCALE, my * game.MOUSE_SCALE)
                if self.hit_box.collidepoint(scaled_pos):
                    game.event_list.remove(e)  # 一個按下事件只會讓一個 button 被按下 
                    self.__isPressed = True
            if e.type == pg.MOUSEBUTTONUP and e.button == 1 and self.__isPressed:
                mx, my = e.pos
                scaled_pos = (mx * game.MOUSE_SCALE, my * game.MOUSE_SCALE)
                self.__isPressed = False
                if self.hit_box.collidepoint(scaled_pos):
                    game.event_list.remove(e)  # 一個放開事件只會讓一個 button 被放開
                    self.__click()
            if e.type == Event_Manager.EVENT_SHAKE:
                x, y = self.rect.center
                delta = 5
                self.moveTo((x, y - delta), 50, False)
                # self.moveTo((x + delta, y + delta), 50, False)
                self.moveTo((x, y), 50, False)

    def check_hover(self):
        mx, my = pg.mouse.get_pos()
        scaled_pos = (mx * game.MOUSE_SCALE, my * game.MOUSE_SCALE)
        if self.hit_box.collidepoint(scaled_pos):
            self.mouse_enter = not self.is_hover  # 還沒hover過的話，觸發進入flag
            self.mouse_exit = False
            self.is_hover = True
        else:
            self.mouse_exit = self.is_hover  # 上一幀還hover的話，觸發離開flag
            self.mouse_enter = False         # 重要，沒加會錯，我猜是因為一幀內出去又離開會來不及把它用上面那個變False
            self.is_hover = False

    # override
    def update(self):
        self.check_hover()
        self.__pressed_effect()
        super().update()

    def setClick(self,func:Callable[[], None] = lambda: None):
        """設定`_click`
        """
        self.__click = func

    def __pressed_effect(self):
        if not self.can_press:
            return
        if ((not self.__isPressed and self.scale_for_transform >= self.ori_scale) or                            # 未按下且已回復原尺寸 (多數情況所以放條件判斷前面)
                (self.__isPressed and self.scale_for_transform <= self.ori_scale * (1 - self.__delta_press_scale))):  # 已按下且已縮放到位
            return

        # 按下縮小、放開放大
        self.transform(scale=self.scale_for_transform + self.__delta_press_scale * self.__press_scale_speed * (-1 if self.__isPressed else 1))

    def transform(self, x=None, y=None, scale=None):
        if scale != None:
            self.scale_for_transform = scale
            self.width = self.__ori_w * scale
            self.height = self.__ori_h * scale
            self.image = pg.transform.smoothscale(self.__ori_image, (self.width, self.height))
            self.rect.size = self.image.get_size()
        if x != None:
            self.x = x
        if y != None:
            self.y = y
    
    def rotate(self, angle):
        self.image = pg.transform.rotate(self.image, angle)

    def set_ori_image(self, img:pg.surface.Surface):
        center = self.rect.center
        self.__ori_image = img
        self.image = self.__ori_image
        self.rect.size = self.__ori_image.get_rect().size
        self.__ori_w, self.__ori_h = self.rect.size
        self.width, self.height = self.rect.size
        self.rect.center = center
        self.hit_box = self.rect.copy()
        
    def set_color(self, color):
        self.image.fill(color)
        self.__ori_image = self.image.copy()
        self.rect.size = self.image.get_rect().size
        self.__ori_w, self.__ori_h = self.rect.size
        self.hit_box = self.rect.copy()