import pygame as pg
import game
from .state import State
from ..object.card import Card
from ..object import Text_Button
from ..object import Carousel
from ..object import Group
from ..object import Confirm_Quit_Object
from ..manager import Font_Manager


class Train_Select_Level_State(State):
    """首頁狀態。繼承自`State`。

    在結構子中，創建`all_sprites`(sprite.Group)，以管理所有首頁會出現的`Object`物件，其他頁面都可以參照這個做法。

    覆寫`update()`時，呼叫`all_sprites.update()`，此時會呼叫我們在`Object`中覆寫的`update()`。

    覆寫`render()`時，呼叫`game.draw_text()`，可以寫文字，並且呼叫`all_sprites.draw()`，此時會根據Object中的rect的資訊，畫出Object中的image。

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
    
    """

    def __init__(self):
        self.all_sprites = Group()
        
        # 建立返回首頁按鈕
        from . import Menu_State, Train_Select_Mode_State
        self.confirm_quit_object = Confirm_Quit_Object(lambda:game.change_state(Menu_State()))
        menu_button = Text_Button(pos=(100, 100), text='首頁')
        menu_button.setClick(lambda: self.confirm_quit_object.set_show(True))
        self.all_sprites.add(menu_button)

        # 選擇 Level 1~6
        for i in range(6):
            btn = Text_Button(pos=(game.CANVAS_WIDTH/2-300+600*(i%2), 400 + i//2*200), text="LEVEL"+str(i+1))
            btn.setClick(lambda level=i+1: game.change_state(Train_Select_Mode_State(level)))
            self.all_sprites.add(btn)

    # override
    def handle_event(self):
        self.confirm_quit_object.handle_event()
        self.all_sprites.handle_event()

    # override
    def update(self):
        self.confirm_quit_object.update()
        self.all_sprites.update()

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "練功坊", 70, game.CANVAS_WIDTH/2, 100)
        self.all_sprites.draw(game.canvas)

        self.confirm_quit_object.render()
