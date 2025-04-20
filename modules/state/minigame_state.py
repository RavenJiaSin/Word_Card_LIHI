import pygame as pg
import game
from .state import State
from ..object import Text_Button
from ..object import Card

class Minigame_State(State):
    """小遊戲狀態。繼承自`State`。

    連連看小遊戲，玩家在這邊可以玩連連看    

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
        
    """
    def __init__(self):
        from .menu_state import Menu_State    # 在這邊import是為了避免circular import
        self.all_sprites = pg.sprite.Group()

        menu_button = Text_Button(pos=(100,100), size=(160,80), text='返回', font_size=40, font='SWEISANSCJKTC-REGULAR')
        menu_button.setClick(lambda:game.change_state(Menu_State()))
        self.all_sprites.add(menu_button)

        card = Card(pos=(game.CANVAS_WIDTH/2, 400), size=200)
        self.all_sprites.add(card)

    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        game.draw_text(game.canvas, "連連看", 70, game.CANVAS_WIDTH/2, 100)
        self.all_sprites.draw(game.canvas)