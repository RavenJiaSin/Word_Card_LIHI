import pygame as pg
import game
from .state import State
from ..object import Text_Button
from ..object import Card
from ..object import Match_Game

class Match_Game_State(State):
    """小遊戲頁面。繼承自`State`。

    找出相應卡片的小遊戲

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
        
    """
    def __init__(self):
        self.all_sprites = pg.sprite.Group()

        menu_button = Text_Button(pos=(100,100), size=(160,80), text='返回', font_size=40, font='SWEISANSCJKTC-REGULAR')
        from .menu_state import Menu_State
        menu_button.setClick(lambda:game.change_state(Menu_State()))
        self.all_sprites.add(menu_button)

        lianliankan = Match_Game()
        self.all_sprites.add(lianliankan.getGroup())

        

    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        game.draw_text(game.canvas, "連連看", 70, game.CANVAS_WIDTH/2, 100)
        self.all_sprites.draw(game.canvas)