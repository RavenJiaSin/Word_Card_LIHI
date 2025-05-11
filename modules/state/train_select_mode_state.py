import pygame as pg
import game
from .state import State
from ..object import Text_Button
from ..object import Group
from ..object import Confirm_Quit_Object
from ..manager import Font_Manager
from ..manager import Train_Enum

class Train_Select_Mode_State(State):
    """練功坊選擇題型頁面，繼承自`State`

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
    
    """

    def __init__(self, level:int):

        self.all_sprites = Group()
        
        # 建立返回首頁按鈕
        from . import Menu_State, Train_Play_State
        self.confirm_quit_object = Confirm_Quit_Object(lambda:game.change_state(Menu_State()))
        menu_button = Text_Button(pos=(100, 100), text='首頁')
        menu_button.setClick(lambda: self.confirm_quit_object.set_show(True))
        self.all_sprites.add(menu_button)

        # 模式選擇按鈕
        btn1 = Text_Button(pos=(game.CANVAS_WIDTH/2, 400), text="單字中翻英")
        btn1.setClick(lambda: game.change_state(Train_Play_State(level, Train_Enum.CHI2ENG)))
        self.all_sprites.add(btn1)

        btn2 = Text_Button(pos=(game.CANVAS_WIDTH/2, 600), text="單字英翻中")
        btn2.setClick(lambda: game.change_state(Train_Play_State(level, Train_Enum.ENG2CHI)))
        self.all_sprites.add(btn2)

        btn3 = Text_Button(pos=(game.CANVAS_WIDTH/2, 800), text="例句填空", font_size=70)
        btn3.setClick(lambda: game.change_state(Train_Play_State(level, Train_Enum.SENTENCE)))
        self.all_sprites.add(btn3)


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
