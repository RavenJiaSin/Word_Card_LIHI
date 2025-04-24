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
        self.__vel = (0,0)
        self.__target_pos = (0,0)
        
    def __handle_event(self):
        """需要覆寫,物件可以從這邊處理相關事件(event_list)
        """
        ...

    def update(self):     
        """需要覆寫,物件在此更新,要記得呼叫__handle_event()才能夠處理事件
        """   
        self.__handle_event()
        self.__move()
        self.rect.center = (int(self.x), int(self.y))

    def moveTo(self, target:tuple, time:int):
        self.__is_moving = True
        self.__target_pos = target
        dir = (target[0]-self.x, target[1]-self.y)
        distance = math.sqrt(dir[0]**2+dir[1]**2)
        speed = distance / (time*1000)
        self.__vel = (dir[0] / distance * speed * game.deltaTick, dir[1] / distance * speed * game.deltaTick)

    def __move(self):
        if not self.__is_moving:
            return
        # 由於按鈕物件會晃動，採用區域確認是否抵達目的地，導致不準確
        dx = self.x - self.__target_pos[0]
        dy = self.y - self.__target_pos[1]
        if abs(dx) < 10 and abs(dy) < 10:
            self.__is_moving = False
            self.__vel = (0,0)
            self.__target_pos = (0,0)
        self.x += self.__vel[0]
        self.y += self.__vel[1]

