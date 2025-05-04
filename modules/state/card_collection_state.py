import pygame as pg
import game
from .state import State
from ..object import Button
from ..object import Text_Button
from ..object import Card
from ..object import Group
from functools import partial
from ..manager import Font_Manager
from modules.database import VocabularyDB

class Card_Collection_State(State):

    def __init__(self):

        self.db = VocabularyDB()
        self.current_vocab_index = 0

        from . import Menu_State  # 在這邊import是為了避免circular import
        self.background_cards = Group()
        self.ui_sprites = Group()
        self.foreground_card = None

        self.scroll_offset = 0  # 初始卷軸偏移
        self.card_list = []

        menu_button = Text_Button(pos=(100, 100), text='首頁')
        menu_button.setClick(lambda:game.change_state(Menu_State()))
        self.ui_sprites.add(menu_button)

        self.card_width = 300
        self.card_height = 400
        self.cards_per_row = 5
        
        self.total_rows = 2
        self.generate_row(0)
        self.generate_row(1)

    def generate_row(self, row_index):
        """生成一整排卡片,row_index從0開始"""

        for col in range(self.cards_per_row):
        
            voc_id = self.db.find_vocabulary(column='Vocabulary')[self.current_vocab_index]['Vocabulary'] # 或你要其他欄位

            x = 330 + col * self.card_width
            y = 180 + row_index * self.card_height
            card = Card(pos=(x, y), scale=2,id=voc_id)
            card.original_x = x
            card.original_y = y
            card.setClick(partial(self.enlarge_card, card.get_id()))
            self.background_cards.add(card)
            self.card_list.append(card)

            self.current_vocab_index += 1    

    def enlarge_card(self, card_id):
        if self.foreground_card:
            self.foreground_card = None
        else:
            self.foreground_card = Card(pos=(game.CANVAS_WIDTH/2, game.CANVAS_HEIGHT/2), scale=3,id=card_id)

    # override
    def handle_event(self):    
        # 有放大卡，檢查點擊位置，不在卡片上就關掉
        if self.foreground_card:
            self.foreground_card.handle_event()
            for event in game.event_list:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    scaled_pos = (mx * game.MOUSE_SCALE, my * game.MOUSE_SCALE)
                    if not self.foreground_card.rect.collidepoint(scaled_pos):
                        self.foreground_card = None
        # 沒有放大卡，則先檢查是否點到背景卡牌或 UI 按鈕
        else:
            self.ui_sprites.handle_event()
            self.background_cards.handle_event()          
            for event in game.event_list:
                # 若為滾輪(上下滾)，計算滾動值
                if event.type == pg.MOUSEWHEEL:
                    self.scroll_offset += event.y * 30
                    if self.scroll_offset > 0:
                        self.scroll_offset = 0
                    
    # override
    def update(self):
        self.background_cards.update()
        self.ui_sprites.update()
        if self.foreground_card:
            self.foreground_card.update()

        max_original_y = max(card.original_y for card in self.card_list)
        if max_original_y + self.scroll_offset < game.CANVAS_HEIGHT:
            self.total_rows += 1
            self.generate_row(self.total_rows - 1)

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "Card Collection", 70, game.CANVAS_WIDTH/2 + 50 , 100)
        self.ui_sprites.draw(game.canvas)

        self.render_background()
        self.render_foreground()
        
    def render_background(self):
        title_area_bottom = 150
        bottom_limit = game.CANVAS_HEIGHT - 50

        for card in self.card_list:
            card.rect.x = card.original_x
            card.rect.y = card.original_y + self.scroll_offset

        background_cards_list = []
        for card in self.background_cards:
            if card.rect.bottom > title_area_bottom and card.rect.top < bottom_limit:

                visible_rect = card.rect.clip(pg.Rect(
                0, title_area_bottom,
                game.CANVAS_WIDTH, bottom_limit - title_area_bottom
                ))
                
                if visible_rect.width > 0 and visible_rect.height > 0:
                # 計算這張卡片圖像中要取的部分
                    source_area = pg.Rect(
                        visible_rect.x - card.rect.x,  # 相對於卡片圖片的位置
                        visible_rect.y - card.rect.y,
                        visible_rect.width,
                        visible_rect.height
                    )
                    background_cards_list.append((card.image, visible_rect.topleft, source_area))
        game.canvas.blits(background_cards_list)

    def render_foreground(self):
        if self.foreground_card:
            dark_overlay = pg.Surface((game.CANVAS_WIDTH, game.CANVAS_HEIGHT), flags=pg.SRCALPHA) #黑幕頁面，製造聚焦效果
            dark_overlay.fill((0, 0, 0, 180))  # RGBA，最後一個值是透明度（0~255）
            game.canvas.blits([(dark_overlay, (0, 0)), (self.foreground_card.image, self.foreground_card.rect)])  # 把暗幕以及放大卡片畫上去