import pygame as pg
import game
from .state import State
from ..object import Text_Button
from ..object import Match_Game
from ..object import Group
from ..manager import Font_Manager


class Match_Game_State(State):
    """小遊戲頁面。繼承自`State`。

    找出相應卡片的小遊戲

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
        match_game (Match_Game): 小遊戲
        
    """
    def __init__(self):
        self.ui_sprites = Group()

        menu_button = Text_Button(pos=(100,100), scale=1, text='返回', font_size=40)
        
        menu_button.setClick(lambda:Match_Game_State.go_to_menu())
        self.ui_sprites.add(menu_button)

        self.match_game = Match_Game()
    
    # overrride
    def handle_event(self):
        self.match_game.handle_event()
        self.ui_sprites.handle_event()
    
    # override
    def update(self):
        self.match_game.update()
        self.ui_sprites.update()

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "連連看", 70, game.CANVAS_WIDTH/2, 100)
        scores = self.match_game.getScore()
        Font_Manager.draw_text(game.canvas, "藍方:"+str(scores[0])+"分", 60, game.CANVAS_WIDTH/2 - 400, 100)
        Font_Manager.draw_text(game.canvas, "紅方:"+str(scores[1])+"分", 60, game.CANVAS_WIDTH/2 + 400, 100)
        self.match_game.getSpriteGroup().draw(game.canvas)
        self.ui_sprites.draw(game.canvas)

    def go_to_menu():
        game.background_color = (30,30,30)
        from .menu_state import Menu_State
        game.change_state(Menu_State())