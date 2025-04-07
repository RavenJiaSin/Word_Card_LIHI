import pygame as pg
import game
from .state import State
from ..object import Button
from ..object import Card
from ..manager import img_map

class Test_State(State):

    def __init__(self):
        from ..state import Menu_State  # 在這邊import是為了避免circular import
        self.all_sprites = pg.sprite.Group()

        menu_button = Button(pos=(game.WINDOW_WIDTH/2,game.WINDOW_HEIGHT/2+100), size=(80,60))
        menu_button.setClick(lambda:game.chage_state(Menu_State()))
        self.all_sprites.add(menu_button)

        card = Card(pos=(game.WINDOW_WIDTH/2, 200), size=100, img=img_map['test_poker'])
        self.all_sprites.add(card)

    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        game.draw_text(game.window, "Test", 50, game.WINDOW_WIDTH/2, 50)
        self.all_sprites.draw(game.window)