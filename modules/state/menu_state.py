import random
import pygame as pg
import game
from modules.database.userDBconnect import UserDB
from modules.database.vocsDBconnect import VocabularyDB
from . import State
from ..object.card import Card
from ..object import Text_Button
from ..object import Carousel
from ..object import Group
from ..manager import Font_Manager
from ..manager import Event_Manager


class Menu_State(State):
    """首頁狀態。繼承自`State`。

    在結構子中，創建`all_sprites`(sprite.Group)，以管理所有首頁會出現的`Object`物件，其他頁面都可以參照這個做法。

    覆寫`update()`時，呼叫`all_sprites.update()`，此時會呼叫我們在`Object`中覆寫的`update()`。

    覆寫`render()`時，呼叫`game.draw_text()`，可以寫文字，並且呼叫`all_sprites.draw()`，此時會根據Object中的rect的資訊，畫出Object中的image。

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
    
    """

    def __init__(self):


        self.all_sprites = Group()

        button_x = 300

        train_button = Text_Button(pos=(button_x, game.CANVAS_HEIGHT / 6 * 1.5), text='練功坊')
        from . import Train_Select_Level_State
        train_button.setClick(lambda:game.change_state(Train_Select_Level_State()))
        self.all_sprites.add(train_button)

        match_button = Text_Button(pos=(button_x, game.CANVAS_HEIGHT / 6 * 2.5), text='連連看')
        from . import Match_Game_State
        match_button.setClick(lambda:game.change_state(Match_Game_State()))
        self.all_sprites.add(match_button)

        card_collection_button = Text_Button(pos=(button_x, game.CANVAS_HEIGHT / 6 * 3.5), text='卡牌庫')
        from . import Card_Collection_State
        card_collection_button.setClick(lambda:game.change_state(Card_Collection_State()))
        self.all_sprites.add(card_collection_button)

        statistic_button = Text_Button(pos=(button_x, game.CANVAS_HEIGHT / 6 * 4.5), text='統　計')
        from . import Statistics_State
        statistic_button.setClick(lambda:game.change_state(Statistics_State()))
        self.all_sprites.add(statistic_button)

        exit_button = Text_Button(pos=(game.CANVAS_WIDTH-100,game.CANVAS_HEIGHT-80), text='EXIT')
        exit_button.setClick(lambda:pg.event.post(pg.event.Event(pg.QUIT)))
        self.all_sprites.add(exit_button)

        self.card_pack_pos = (game.CANVAS_WIDTH / 2 + 100, game.CANVAS_HEIGHT / 2) 

        self.card_packet_button = Card(pos=self.card_pack_pos, scale=2, id='2812_pack')
        self.card_packet_button.setClick(self.open_card_pack)
        self.card_packet_button.setWiggle()
        if not game.opened_today_cards:
            self.all_sprites.add(self.card_packet_button)

        self.daily_card = Carousel(center=self.card_pack_pos)

    def open_card_pack(self):
        game.opened_today_cards = True
        self.all_sprites.remove(self.card_packet_button)
        
    # override
    def handle_event(self):
        self.all_sprites.handle_event()
        if game.opened_today_cards:
            self.daily_card.handle_event()
        for e in game.event_list:
            if e.type == Event_Manager.EVENT_ANEWDAY:
                self.all_sprites.add(self.card_packet_button)
                self.daily_card = Carousel(center=self.card_pack_pos)

            if e.type == pg.KEYDOWN:
                if e.key == pg.K_RSHIFT:
                    db = VocabularyDB()
                    user_db = UserDB()
                    # k = random.sample(db.find_vocabulary('id', level=1), 10)
                    k = random.sample(db.find_vocabulary('id', level=1), 50) + random.sample(db.find_vocabulary('id', level=2), 10)\
                        + random.sample(db.find_vocabulary('id', level=3), 10) + random.sample(db.find_vocabulary('id', level=4), 10)\
                        + random.sample(db.find_vocabulary('id', level=5), 10) + random.sample(db.find_vocabulary('id', level=6), 10)
                    for word in k:
                        user_db.add_card_to_user(game.USER_ID, word['ID'])
                        user_db.update_card_info(game.USER_ID, word['ID'], proficiency=random.randint(1,6))


    # override
    def update(self):
        self.all_sprites.update()
        if game.opened_today_cards:
            self.daily_card.update()

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "首頁", 70, game.CANVAS_WIDTH/2, 100)
        self.all_sprites.draw(game.canvas)
        if game.opened_today_cards:
            self.daily_card.draw(game.canvas)
