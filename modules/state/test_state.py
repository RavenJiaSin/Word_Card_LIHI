import pygame as pg
import game
from .state import State
from ..object import Text_Button
from ..object import Card

class Test_State(State):

    def __init__(self):
        from ..state import Main_State  # 在這邊import是為了避免circular import
        self.all_sprites = pg.sprite.Group()

        menu_button = Text_Button(pos=(game.CANVAS_WIDTH/2,game.CANVAS_HEIGHT/2+100), size=(80,40), text='Main', font_size=20)
        menu_button.setClick(lambda:game.change_state(Main_State()))
        self.all_sprites.add(menu_button)

        card = Card(pos=(game.CANVAS_WIDTH/2, 200), size=100, id='test_poker')
        self.all_sprites.add(card)


    # override
    def handle_event(self):
        ...
    
    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        game.draw_text(game.canvas, "Test", 50, game.CANVAS_WIDTH/2, 50)
        self.all_sprites.draw(game.canvas)