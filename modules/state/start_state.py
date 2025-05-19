import random
import pygame as pg
import game
from .state import State
from ..manager import Font_Manager
from ..object import Text_Button
from ..object import Card
from ..object import Group
from ..object import Toggle_Button
from modules.database import VocabularyDB

class Start_State(State):
    """初始狀態。繼承自`State`。
    
    """
    def __init__(self):
        self.all_sprites = Group()
        
        from ..state import Menu_State
        db = VocabularyDB()

        start_card = Card((-500, game.CANVAS_HEIGHT/2), 3, db.find_vocabulary(Vocabulary='start')[0]['ID'])
        start_card.setWiggle()
        start_card.moveTo((game.CANVAS_WIDTH/2-300, game.CANVAS_HEIGHT/2+100), 1000)
        start_card.setClick(lambda:game.change_state(Menu_State()))
        self.all_sprites.add(start_card)

        quit_card = Card((game.CANVAS_WIDTH+500, game.CANVAS_HEIGHT/2), 3, db.find_vocabulary(Vocabulary='quit')[0]['ID'])
        quit_card.setWiggle()
        quit_card.moveTo((game.CANVAS_WIDTH/2+300, game.CANVAS_HEIGHT/2+100), 1000)
        quit_card.setClick(lambda:pg.event.post(pg.event.Event(pg.QUIT)))

        self.all_sprites.add(quit_card)

        # enter_button = Text_Button(pos=(game.CANVAS_WIDTH/2,game.CANVAS_HEIGHT/2+50), text='開始')
        # quit_button = Text_Button(pos=(game.CANVAS_WIDTH/2,game.CANVAS_HEIGHT/2+200), text='退出')
        # from ..state import Menu_State # 在這邊import是為了避免circular import
        # enter_button.setClick(lambda:game.change_state(Menu_State()))
        # quit_button.setClick(lambda:pg.event.post(pg.event.Event(pg.QUIT)))
        # self.all_sprites.add(enter_button)
        # self.all_sprites.add(quit_button)

        # random_word = random.sample(db.find_vocabulary()[0:900], 1)[0]['ID']
        # self.tmp_card = Card((300, game.CANVAS_HEIGHT/2), 3, random_word)
        # self.tmp_card.setWiggle()
        # self.all_sprites.add(self.tmp_card)
    # override 
    def handle_event(self):
        self.all_sprites.handle_event()


    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "WORD卡厲害", 150, game.CANVAS_WIDTH/2, 200)
        self.all_sprites.draw(game.canvas)