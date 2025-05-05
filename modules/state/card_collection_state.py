import pygame as pg
import game
from .state import State
from ..object import Button
from ..object import Text_Button
from ..object import Card
from ..object import Group
from ..object import Card_Info
from ..object import Toggle_Button
from functools import partial
from ..manager import Font_Manager
from modules.database import VocabularyDB

class Card_Collection_State(State):

    def __init__(self):

        self.db = VocabularyDB()
        self.current_vocab_index = 0
        self.vocab_list = self.db.get_all()

        self.filter_ui_visible = False  # 篩選器畫面是否顯示

        from . import Menu_State  # 在這邊import是為了避免circular import
        self.background_cards = Group()
        self.ui_sprites = Group()
        self.filter_ui_sprites = Group()  # 裡面放 toggle_button 等 UI
        self.foreground_card = None
        self.foreground_card_info = None

        self.scroll_offset = 0  # 初始卷軸偏移

        menu_button = Text_Button(pos=(100, 100), text='首頁')
        menu_button.setClick(lambda:game.change_state(Menu_State()))
        self.ui_sprites.add(menu_button)

        filter_button = Text_Button(pos=(300, 100),text='篩選器',font_size=40)
        filter_button.setClick(lambda: self.toggle_filter_ui(True))
        self.ui_sprites.add(filter_button)

        #詞性篩選器按鈕
        self.toggle_buttons = {}

        type_labels = ['n.', 'v.', 'adj.', 'adv.', 'prep.', 'conj.','']
        type_start_x = 270
        type_y = game.CANVAS_HEIGHT/2 - 200
        for i, label in enumerate(type_labels):
            btn = Toggle_Button(pos=(type_start_x + i * 230, type_y), scale=1)
            self.toggle_buttons[label] = btn
            self.filter_ui_sprites.add(btn)

        #等級篩選器按鈕
        self.toggle_buttons_level = {}

        level_y = game.CANVAS_HEIGHT/2 + 200
        for i in range(6):  # Level 1~6
            level = i + 1
            btn = Toggle_Button(pos=(350 + i * 250, level_y), scale=1)
            self.toggle_buttons_level[level] = btn
            self.filter_ui_sprites.add(btn)

        apply_button = Text_Button(pos=(game.CANVAS_WIDTH/2, game.CANVAS_HEIGHT-100), text='完成')
        apply_button.setClick(lambda: self.apply_filter())
        self.filter_ui_sprites.add(apply_button)

        self.card_width = 300
        self.card_height = 400
        self.cards_per_row = 5
        
        self.total_rows = 2
        self.generate_row(0)
        self.generate_row(1)

    def toggle_filter_ui(self, show: bool):
        self.filter_ui_visible = show

    def apply_filter(self):
        self.filter_ui_visible = False
        self.background_cards.empty()
        self.current_vocab_index = 0

        self.scroll_offset = 0

        self.generate_row(0)
        self.generate_row(1)
        self.total_rows = 2

    def vocab_filter(self,vocab_data):
        part = vocab_data['Part_of_speech']
        level = vocab_data['Level']
        
        type_filter_active = any(btn.get() for btn in self.toggle_buttons.values())
        level_filter_active = any(btn.get() for btn in self.toggle_buttons_level.values())

        if (not type_filter_active) or (not level_filter_active):
            return False

        type_cond = self.toggle_buttons[part].get()
        level_cond = self.toggle_buttons_level[level].get()

        return type_cond and level_cond

    def generate_row(self, row_index):

        col = 0

        """生成一整排卡片,row_index從0開始"""
        while col < self.cards_per_row and self.current_vocab_index < len(self.vocab_list):
            voc_data = self.vocab_list[self.current_vocab_index]

            passed = self.vocab_filter(voc_data)

            if passed:
                voc_id = voc_data['ID']
                x = 330 + col * self.card_width
                y = 350 + row_index * self.card_height
                card = Card(pos=(x, y), scale=2,id=voc_id)
                card.ori_y = y
                card.setClick(partial(self.enlarge_card, card.get_id()))
                self.background_cards.add(card)
                col += 1

            self.current_vocab_index += 1   

    def enlarge_card(self, card_id):
        if self.foreground_card:
            self.foreground_card = None
            self.foreground_card_info = None
        else:
            self.foreground_card = Card(pos=(game.CANVAS_WIDTH/2-400, game.CANVAS_HEIGHT/2), scale=4,id=card_id)
            self.foreground_card_info = Card_Info((game.CANVAS_WIDTH/2+360, 500), 3, card_id)

    # override
    def handle_event(self):    
        if self.filter_ui_visible:
            self.filter_ui_sprites.handle_event()
            return

        # 有放大卡，檢查點擊位置，不在卡片上就關掉
        if self.foreground_card:
            self.foreground_card.handle_event()
            for event in game.event_list:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    scaled_pos = (mx * game.MOUSE_SCALE, my * game.MOUSE_SCALE)
                    if not self.foreground_card.rect.collidepoint(scaled_pos) and not self.foreground_card_info.rect.collidepoint(scaled_pos):
                        self.foreground_card = None
                        self.foreground_card_info = None
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
        if self.filter_ui_visible:
            self.filter_ui_sprites.update()

        self.background_cards.update()
       
        for card in self.background_cards:
            card.rect.centery = card.ori_y + self.scroll_offset

        self.ui_sprites.update()
        if self.foreground_card:
            self.foreground_card.update()
            self.foreground_card_info.update()

        if self.background_cards:
            max_original_y = max(card.ori_y for card in self.background_cards)
            if max_original_y + self.scroll_offset < game.CANVAS_HEIGHT:
                self.total_rows += 1
                self.generate_row(self.total_rows - 1)

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "Card Collection", 70, game.CANVAS_WIDTH/2 + 50 , 100)
        self.ui_sprites.draw(game.canvas)

        self.render_background()
        self.render_foreground()
        self.render_filter_ui()
        
    def render_background(self):
        show_card_top = 150
        show_card_bottom = game.CANVAS_HEIGHT - 50

        # 進行卡片畫面截斷
        background_cards_list = []
        for card in self.background_cards:
            # 卡片在顯示區域中
            if card.rect.bottom > show_card_top and card.rect.top < show_card_bottom:

                visible_rect = card.rect.clip(pg.Rect(
                0, show_card_top,
                game.CANVAS_WIDTH, show_card_bottom - show_card_top
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
        if not self.foreground_card:
            return
        
        dark_overlay = pg.Surface((game.CANVAS_WIDTH, game.CANVAS_HEIGHT), flags=pg.SRCALPHA) #黑幕頁面，製造聚焦效果
        dark_overlay.fill((0, 0, 0, 180))  # RGBA，最後一個值是透明度（0~255）
        game.canvas.blits([(dark_overlay, (0, 0)), (self.foreground_card.image, self.foreground_card.rect), (self.foreground_card_info.image, self.foreground_card_info.rect)])  # 把暗幕以及放大卡片畫上去

    def render_filter_ui(self):
        if self.filter_ui_visible:
            overlay = pg.Surface((game.CANVAS_WIDTH, game.CANVAS_HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            game.canvas.blit(overlay, (0, 0))

            # 篩選器 UI
            self.filter_ui_sprites.draw(game.canvas)

            for label, button in self.toggle_buttons.items():
                Font_Manager.draw_text(game.canvas,label,40,button.rect.centerx,button.rect.bottom + 10)
            for level,button in self.toggle_buttons_level.items():
                Font_Manager.draw_text(game.canvas,str(level),40,button.rect.centerx,button.rect.bottom + 10)