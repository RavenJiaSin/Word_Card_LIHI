import pygame as pg
import game
from .state import State
from ..object import Text_Button
from ..manager import Font_Manager
from ..object import Card

class Start_State(State):
    """初始狀態。繼承自`State`。
    
    """
    def __init__(self):
        from ..state import Menu_State # 在這邊import是為了避免circular import
        self.__menu_state = Menu_State()

        self.all_sprites = pg.sprite.Group()

        enter_button = Text_Button(pos=(game.CANVAS_WIDTH/2,game.CANVAS_HEIGHT/2+50), scale=1, text='ENTER', font_size=40)
        enter_button.setClick(lambda:game.change_state(self.__menu_state))

        self.all_sprites.add(enter_button)
        apple_card = Card((300, game.CANVAS_HEIGHT/2), 3, 'apple')
        apple_card.setWiggle()
        self.all_sprites.add(apple_card)
    
    # override 
    def handle_event(self):
        for event in game.event_list:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    game.change_state(self.__menu_state)


    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "WORD卡厲害", 100, game.CANVAS_WIDTH/2, 200)
        self.all_sprites.draw(game.canvas)
