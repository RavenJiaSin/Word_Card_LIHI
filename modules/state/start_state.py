import pygame as pg
import game
from .state import State
from ..object import Text_Button
from ..manager import Font_Manager
from ..object import Card
from ..object import Group

class Start_State(State):
    """初始狀態。繼承自`State`。
    
    """
    def __init__(self):
        self.all_sprites = Group()

        enter_button = Text_Button(pos=(game.CANVAS_WIDTH/2,game.CANVAS_HEIGHT/2+50), text='開始')
        quit_button = Text_Button(pos=(game.CANVAS_WIDTH/2,game.CANVAS_HEIGHT/2+200), text='退出')
        from ..state import Menu_State # 在這邊import是為了避免circular import
        enter_button.setClick(lambda:game.change_state(Menu_State()))
        quit_button.setClick(lambda:pg.event.post(pg.event.Event(pg.QUIT)))

        self.all_sprites.add(enter_button)
        self.all_sprites.add(quit_button)
        self.apple_card = Card((300, game.CANVAS_HEIGHT/2), 3, 'apple')
        self.apple_card.setWiggle()
        self.all_sprites.add(self.apple_card)
    
    # override 
    def handle_event(self):
        self.all_sprites.handle_event()


    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "WORD卡厲害", 100, game.CANVAS_WIDTH/2, 200)
        self.all_sprites.draw(game.canvas)