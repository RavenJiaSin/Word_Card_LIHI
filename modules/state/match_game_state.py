import pygame as pg
import game
from .state import State
from ..object import Text_Button
from ..object import Match_Game
from ..object import Group
from ..object import Text_Object
from ..manager import Font_Manager
from ..manager import Event_Manager


class Match_Game_State(State):
    """小遊戲頁面。繼承自`State`。

    找出相應卡片的小遊戲

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
        match_game (Match_Game): 小遊戲
        
    """
    def __init__(self):
        self.ui_sprites = Group()

        menu_button = Text_Button(pos=(100,100), text='首頁')
        menu_button.setClick(lambda:self.go_to_menu())
        self.ui_sprites.add(menu_button)

        self.choose_text = Text_Object(pos=(game.CANVAS_WIDTH/2, 300), text="選擇卡片數量", font_size= 80, font_color=(255,255,5))
        self.ui_sprites.add(self.choose_text)

        self.difficulty_button_map = {'easy':(Text_Button(pos=(game.CANVAS_WIDTH/2-500, game.CANVAS_HEIGHT/2), text='3x4', font_color=(0,255,0)), 3),
                                      'medium':(Text_Button(pos=(game.CANVAS_WIDTH/2, game.CANVAS_HEIGHT/2), text='4x4', font_color=(200,200,0)), 4),
                                      'hard':(Text_Button(pos=(game.CANVAS_WIDTH/2+500, game.CANVAS_HEIGHT/2), text='5x4', font_color=(255,0,0)),5)}
        
        [(btn[0].setWiggle(), btn[0].setClick(lambda cols=btn[1]:self.start_match_game(cols)), self.ui_sprites.add(btn[0])) for btn in self.difficulty_button_map.values()]

        self.match_game = None
    
    # overrride
    def handle_event(self):
        for event in game.event_list:
            if event.type == Event_Manager.EVENT_MATCH_GAME_FINISH:
                winner = event.dict.get('winner', 'ERROR')
                self.show_match_game_result(winner)

        if self.match_game:
            self.match_game.handle_event()
        self.ui_sprites.handle_event()
    
    # override
    def update(self):
        if self.match_game:
            self.match_game.update()
        self.ui_sprites.update()

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "連連看", 70, game.CANVAS_WIDTH/2, 100)
        if self.match_game:
            self.match_game.render()
        self.ui_sprites.draw(game.canvas)


    def start_match_game(self, cols):
        self.choose_text.kill()
        self.match_game = Match_Game(cols=cols, pos=(game.CANVAS_WIDTH/2,game.CANVAS_HEIGHT/2+50))
        [btn[0].kill() for btn in self.difficulty_button_map.values()]

    def show_match_game_result(self, winner):
        self.result_text = Text_Object((game.CANVAS_WIDTH/2, game.CANVAS_HEIGHT/2), winner+'獲勝!', 80)
        self.replay_button = Text_Button(pos=(game.CANVAS_WIDTH/2, game.CANVAS_HEIGHT/2+200), text='重玩')
        self.replay_button.setClick(lambda:self.quit_match_game())
        self.ui_sprites.add(self.result_text)
        self.ui_sprites.add(self.replay_button)

    def quit_match_game(self):
        self.match_game = None
        self.result_text.kill()
        self.replay_button.kill()
        self.choose_text.add(self.ui_sprites)
        [self.ui_sprites.add(btn[0]) for btn in self.difficulty_button_map.values()]


    def go_to_menu(self):
        self.match_game = None
        from .menu_state import Menu_State
        game.change_state(Menu_State())