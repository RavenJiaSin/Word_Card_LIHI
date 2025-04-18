import pygame as pg
import game
from .state import State
from ..object import Button

class Main_State(State):
    """主頁狀態。繼承自`State`。
    
    """
    def __init__(self):
        from ..state import Test_State # 在這邊import是為了避免circular import

        self.all_sprites = pg.sprite.Group()

        test_button = Button(pos=(game.WINDOW_WIDTH/2,game.WINDOW_HEIGHT/2), size=(80,60))

        test_button.setClick(lambda:game.chage_state(Test_State()))
        self.all_sprites.add(test_button)

        exit_button = Button(pos=(game.WINDOW_WIDTH/2,game.WINDOW_HEIGHT/2+100), size=(80,60))
        exit_button.setClick(lambda:pg.event.post(pg.event.Event(pg.QUIT)))
        self.all_sprites.add(exit_button)

        
    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        game.draw_text(game.window, "Main", 50, game.WINDOW_WIDTH/2, 50)
        self.all_sprites.draw(game.window)