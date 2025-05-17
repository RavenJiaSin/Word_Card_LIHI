import pygame as pg
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
        self.hit_box = self.rect.copy()
        self.width = float(self.rect.width)
        self.height = float(self.rect.height)
        self.scale = scale
        self.__is_moving = False
        self.__is_wiggle = False
        self.__goDown = True
        self.__movements = []
        
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

    def moveTo(self, target:tuple, ms:int, hitbox_follow:bool=True):
        '''
        將移動加入佇列

        設定目標位置，在指定時間內移動過去。可決定 hitbox 是否跟著移動
        '''
        movement = {}
        movement['hitbox_follow'] = hitbox_follow
        movement['start_pos'] = self.rect.center if len(self.__movements) == 0 else self.__movements[-1]['end_pos']
        movement['end_pos'] = target
        movement['total_movement'] = (target[0] - movement['start_pos'][0], target[1] - movement['start_pos'][1])
        movement['total_frames'] = max(int(ms / 1000 * game.FPS), 1)  # 最少1幀，這樣才能移動
        movement['cur_frame'] = 0
        self.__movements.append(movement)
        self.__ori_wiggle = self.__is_wiggle
        # self.stopWiggle() # nah. side effect is bad. Will not wiggle if setWiggle() is called while moving

    def __move(self):
        if len(self.__movements) == 0:
            return
        cur_movement = self.__movements[0]
        cur_movement['cur_frame'] += 1
        self.x = cur_movement['start_pos'][0] + (cur_movement['total_movement'][0] * (cur_movement['cur_frame'] / cur_movement['total_frames']))
        self.y = cur_movement['start_pos'][1] + (cur_movement['total_movement'][1] * (cur_movement['cur_frame'] / cur_movement['total_frames']))        
        if cur_movement['hitbox_follow']:
            self.hit_box.center = (int(self.x), int(self.y))
        if cur_movement['cur_frame'] == cur_movement['total_frames']:
            self.__movements.remove(cur_movement)

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
