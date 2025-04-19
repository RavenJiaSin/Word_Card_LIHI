from typing import Callable
import pygame as pg
from .object import Object
import game

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
    def __init__(self, pos:tuple=(0,0), size:tuple=(32,32), img=None):
        super().__init__(pos=pos, size=size, img=img)
        self.__click = lambda:None
        self.__isWiggle = False
        self.__ori_y = self.y
        self.__goDown = True

    # override
    def __handle_event(self):
        for e in game.event_list:
            if e.type == pg.MOUSEBUTTONDOWN:
                if(self.rect.collidepoint(e.pos)):
                    self.__click()
   # override
    def update(self):
        self.__handle_event()
        self.__wiggle()
        super().update()

    def setWiggle(self):
        """開始物件抖動,呼叫stopWiggle()停止
        """
        self.__isWiggle = True
        self.__goDown = True

    def stopWiggle(self):
        """停止物件抖動
        """
        self.__isWiggle = False

    def __wiggle(self):
        """抖動物件
        """
        if not self.__isWiggle:
            return
        wiggleHeight = 0.02
        wiggleFreq = 1.2
        
        maxHeight = wiggleHeight * self.height
        wiggleSpeed = 2 * maxHeight / (1/wiggleFreq)

        if self.y < self.__ori_y + maxHeight and self.__goDown:
            self.y += (wiggleSpeed * game.deltaTick / 1000)
        elif self.y > self.__ori_y - maxHeight:
            self.__goDown = False
            self.y -= (wiggleSpeed * game.deltaTick / 1000)
        else:
            self.__goDown = True


    def setClick(self,func:Callable[[], None] = lambda: None):
        """設定`_click`
        """
        self.__click = func