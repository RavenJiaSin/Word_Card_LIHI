import pygame as pg
import game
from .state import State
from ..object import Button
from ..object import Text_Button


class Start_State(State):
    """初始狀態。繼承自`State`。
    
    """
    def __init__(self):
        from ..state import Menu_State # 在這邊import是為了避免circular import

        self.all_sprites = pg.sprite.Group()

        enter_button = Text_Button(pos=(game.WINDOW_WIDTH/2,game.WINDOW_HEIGHT/2 + 20), size=(80,40), text='ENTER', font_size=20)

        enter_button.setClick(lambda:game.chage_state(Menu_State()))
        self.all_sprites.add(enter_button)
        
    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        game.draw_text(game.window, "WORD卡厲害", 50, game.WINDOW_WIDTH/2, game.WINDOW_HEIGHT/2 - 50)
        self.all_sprites.draw(game.window)