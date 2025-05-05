import pygame as pg
import math
import game

class Object(pg.sprite.Sprite):
    """基礎遊戲物件。繼承自`pg.Sprite`。
    
    要新增新物件類別需要繼承此類別。放入`sprite.Group`中集中管理並在畫面中顯示。範例參考`Menu_State`。

    必須覆寫`_handle_event()`以及`update()`。

    Attributes:
        x (float): 物件水平中心點,使用x控制浮點水平移動,若只需要整數,直接更新`rect.centerx`,在`update()`中更新。範例參考`Button`的`_wiggle()`。
        y (float): 物件垂直中心點,使用y控制浮點垂直移動,同x使用方式(在Pygame中,y-axis向下增加)。
        width (float): 物件寬度。
        height (float): 物件高度。
        image (pg.Surface): 物件渲染在畫面上的圖片。
        rect (pg.Rect): 物件渲染在畫面上的位置、寬高(transform)資訊, x 和 y 更新後要存回`rect`中。
    """
    def __init__(self, pos:tuple=(0,0), scale:float=1, img=None):
        super().__init__()
        self.x = float(pos[0])
        self.y = float(pos[1])
        if img == None:
            self.image = pg.Surface((160,120))
            self.image.fill(pg.Color(200,50,50))
        else:
            width, height = img.get_size()
            self.image = pg.transform.smoothscale(img, (width*scale,height*scale))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.width = float(self.rect.width)
        self.height = float(self.rect.height)
        self.scale = scale
        self.__is_moving = False
        self.__is_wiggle = False
        self.__goDown = True
        
    def handle_event(self):
        """需要覆寫,物件可以從這邊處理相關事件(event_list)
        """
        ...

    def update(self):     
        """需要覆寫,物件在此更新,要記得呼叫__handle_event()才能夠處理事件
        """   
        self.__wiggle()
        self.__move()
        self.rect.center = (int(self.x), int(self.y))

    def moveTo(self, target:tuple, ms:int):
        # .__move_XXX only declared and used in move function. Do not call them from outside
        self.__move_start_pos = self.rect.center
        self.__move_total_movement = (target[0] - self.rect.centerx, target[1] - self.rect.centery)
        self.__move_total_frames = int(ms / 1000 * game.FPS)
        self.__move_cur_frame = 0
        self.__ori_wiggle = self.__is_wiggle
        self.stopWiggle()
        self.__is_moving = True

    def __move(self):
        if not self.__is_moving:
            return
        self.__move_cur_frame += 1
        self.x = self.__move_start_pos[0] + (self.__move_total_movement[0] * (self.__move_cur_frame / self.__move_total_frames))
        self.y = self.__move_start_pos[1] + (self.__move_total_movement[1] * (self.__move_cur_frame / self.__move_total_frames))        
        
        if self.__move_cur_frame == self.__move_total_frames:
            self.__is_moving = False
            if self.__ori_wiggle:
                self.setWiggle()

    def setWiggle(self):
        """開始物件抖動,呼叫stopWiggle()停止
        """
        self.__is_wiggle = True
        self.__goDown = True
        self.__ori_y = self.y

    def stopWiggle(self):
        """停止物件抖動
        """
        self.__is_wiggle = False

    def __wiggle(self):
        """抖動物件
        """
        if not self.__is_wiggle:
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
