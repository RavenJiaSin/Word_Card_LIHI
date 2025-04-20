import pygame as pg
import game
from .state import State
from ..object import Text_Button
from ..object import Card

class Minigame_State(State):

    def __init__(self):
        from ..state import Main_State  # 在這邊import是為了避免circular import
        self.all_sprites = pg.sprite.Group()

        menu_button = Text_Button(pos=(100,100), size=(160,80), text='返回', font_size=40, font='SWEISANSCJKTC-REGULAR')
        menu_button.setClick(lambda:game.change_state(Main_State()))
        self.all_sprites.add(menu_button)

        card = Card(pos=(game.CANVAS_WIDTH/2, 400), size=200)
        self.all_sprites.add(card)

    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        game.draw_text(game.canvas, "連連看", 50, game.CANVAS_WIDTH/2, 50)
        self.all_sprites.draw(game.canvas)