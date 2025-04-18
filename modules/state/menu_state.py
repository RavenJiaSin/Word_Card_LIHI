import pygame as pg
import game
from modules.object.card import Card
from .state import State
from ..object import Button
from ..object import Text_Button
from ..object import Carousel

class Menu_State(State):
    """首頁狀態。繼承自`State`。

    在結構子中，創建`all_sprites`(sprite.Group)，以管理所有首頁會出現的`Object`物件，其他頁面都可以參照這個做法。

    覆寫`update()`時，呼叫`all_sprites.update()`，此時會呼叫我們在`Object`中覆寫的`update()`。

    覆寫`render()`時，呼叫`game.draw_text()`，可以寫文字，並且呼叫`all_sprites.draw()`，此時會根據Object中的rect的資訊，畫出Object中的image。

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
    
    """
    card_pack = True

    def __init__(self):

        self.all_sprites = pg.sprite.Group()

        button_x = 150
        button_wh = (80, 60)

        train_button = Text_Button(pos=(button_x, game.WINDOW_HEIGHT / 6 * 1.5), size=button_wh, text='練功坊')
        # test_button.setClick(lambda:game.chage_state(Test_State()))
        self.all_sprites.add(train_button)

        match_button = Text_Button(pos=(button_x, game.WINDOW_HEIGHT / 6 * 2.5), size=button_wh, text='連連看')
        # match_button.setClick(lambda:game.chage_state(Test_State()))
        self.all_sprites.add(match_button)

        card_collection_button = Text_Button(pos=(button_x, game.WINDOW_HEIGHT / 6 * 3.5), size=button_wh, text='卡牌庫')
        # tcard_collection_button.setClick(lambda:game.chage_state(Test_State()))
        self.all_sprites.add(card_collection_button)

        statistic_button = Text_Button(pos=(button_x, game.WINDOW_HEIGHT / 6 * 4.5), size=button_wh, text='統計資料')
        # statistic_button.setClick(lambda:game.chage_state(Test_State()))
        self.all_sprites.add(statistic_button)

        exit_button = Text_Button(pos=(game.WINDOW_WIDTH-60,game.WINDOW_HEIGHT-60), size=(60,45), text='EXIT', font_size=12)
        exit_button.setClick(lambda:pg.event.post(pg.event.Event(pg.QUIT)))
        self.all_sprites.add(exit_button)

        card_pack_pos = (game.WINDOW_WIDTH / 2 + 100, game.WINDOW_HEIGHT / 2) 

        if self.card_pack:
            self.card_packet_button = Card(pos=card_pack_pos, size=200, name='test_poker')
            self.card_packet_button.setClick(self.open_card_pack)
            self.all_sprites.add(self.card_packet_button)

        self.daily_card = Carousel(center=card_pack_pos, card_size=200, zoom_factor=0.3, speed=1)

    def open_card_pack(self):
        self.card_pack = False
        self.all_sprites.remove(self.card_packet_button)
        
    # override
    def update(self):
        self.all_sprites.update()
        if (not self.card_pack):
            self.daily_card.update()

    # override
    def render(self):
        game.draw_text(game.window, "Menu", 50, game.WINDOW_WIDTH/2, 50)
        self.all_sprites.draw(game.window)
        if (not self.card_pack):
            self.daily_card.draw(game.window)