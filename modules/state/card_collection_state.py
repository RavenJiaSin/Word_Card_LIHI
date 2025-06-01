import pygame as pg
import game
from .state import State
from ..object import Text_Button
from ..object import Card
from ..object import Group
from ..object import Card_Info
from ..object import Toggle_Button
from ..object import Confirm_Quit_Object
from ..object import Text_Sound_Button
from functools import partial
from ..manager import Font_Manager
from ..manager import Event_Manager
from modules.database import VocabularyDB
from modules.database import UserDB

class Card_Collection_State(State):
    """遊戲中卡片收藏頁面的狀態管理類別。

    管理詞彙卡片的顯示、篩選、滾動與互動功能。
    
    Attributes:
        db (VocabularyDB): 詞彙資料庫物件，用於取得所有詞彙。
        current_vocab_index (int): 當前詞彙的索引。
        vocab_list (List[dict]): 包含所有詞彙資料的清單。
        background_cards (pygame.sprite.Group): 背景卡片群組。
        ui_sprites (pygame.sprite.Group): 所有 UI 元件的群組（按鈕等）。
        foreground_card (Card or None): 被選中的卡片（如果有的話）。
        foreground_card_info (dict or None): 被選中卡片的詳細資訊。
        scroll_offset (int): 滾動卷軸的偏移量。
        toggle_button_list (List[Toggle_Button]): 所有篩選器按鈕的列表。
        background_top (int): 背景卡片顯示區域的上邊界。
        background_bottom (int): 背景卡片顯示區域的下邊界。
        card_width (int): 卡片的寬度間距。
        card_height (int): 卡片的高度間距。
        cards_per_row (int): 每一列要顯示的卡片數量。
        total_rows (int): 總列數，用於初始化卡片。
    """

    def __init__(self):
        self.voc_db = VocabularyDB()
        self.user_db = UserDB()
        self.current_vocab_index = 0
        self.vocab_list = []
        for card in self.user_db.get_card_info(game.USER_ID):
            if card['durability'] <= 0:
                continue
            voc_dic = self.voc_db.find_vocabulary(id=card['voc_id'])[0]
            voc_dic['durability'] = int(card['durability'])
            self.vocab_list += [voc_dic]

        self.vocab_list = sorted(self.vocab_list, key=lambda x: x["durability"])

        from . import Menu_State
        self.background_cards = Group()
        self.ui_sprites = Group()
        self.foreground_card = None
        self.foreground_card_info = None
        self.text_sound_button_1 = None
        self.text_sound_button_2 = None

        self.scroll_offset = 0  # 初始卷軸偏移
        
        # 建立返回首頁按鈕
        self.confirm_quit_object = Confirm_Quit_Object(lambda:game.change_state(Menu_State()))
        menu_button = Text_Button(pos=(100, 100), text='首頁')
        menu_button.setClick(lambda: self.confirm_quit_object.set_show(True))
        self.ui_sprites.add(menu_button)

        self.toggle_button_list = []
        self.partofspeech_button_list = []
        self.level_button_list = []

        # 詞性篩選器按鈕
        partofspeech_labels = ['n.', 'v.', 'adj.', 'adv.', 'prep.', 'conj.']
        toggle_start_x = 70
        toggle_start_y = 250
        gap = 100
        for i, label in enumerate(partofspeech_labels):
            btn = Toggle_Button(pos=(toggle_start_x,toggle_start_y+i*gap), scale=0.3, label=label)
            btn.setClick(lambda b=btn: (b.toggle(), self.reset_background_cards()))
            self.ui_sprites.add(btn)
            self.toggle_button_list.append(btn)
            self.partofspeech_button_list.append(btn)

        # 全選詞性按鈕
        btn = Toggle_Button(pos=(toggle_start_x,toggle_start_y+6*gap), scale=0.3, label='')
        btn.setClick(lambda b=btn: (b.toggle(), list(tmp.set_state(b.get_state()) for tmp in self.partofspeech_button_list), self.reset_background_cards()))
        self.ui_sprites.add(btn)

        # 等級篩選器按鈕 Level 1~6
        toggle_start_x = 150
        toggle_start_y = 250
        for i in range(6):
            level = i + 1
            btn = Toggle_Button(pos=(toggle_start_x, toggle_start_y+i*gap), scale=0.3, label=str(level))
            btn.setClick(lambda b=btn: (b.toggle(), self.reset_background_cards()))
            self.ui_sprites.add(btn)
            self.toggle_button_list.append(btn)
            self.level_button_list.append(btn)

        # 全選等級按鈕
        btn = Toggle_Button(pos=(toggle_start_x,toggle_start_y+6*gap), scale=0.3, label='')
        btn.setClick(lambda b=btn: (b.toggle(), list(tmp.set_state(b.get_state()) for tmp in self.level_button_list), self.reset_background_cards()))
        self.ui_sprites.add(btn)

        # 設定卡片顯示範圍與版面
        self.background_top = 200
        self.background_bottom = game.CANVAS_HEIGHT - 50
        self.card_width = 300
        self.card_height = 400
        self.cards_per_row = 5
        
        self.total_rows = 2
        self.generate_row(0)
        self.generate_row(1)

    def reset_background_cards(self):
        self.background_cards.empty()
        self.current_vocab_index = 0

        for i in range(self.total_rows):
            self.generate_row(i)

    def is_pass_vocab_filter(self, vocab_data) -> bool:
        part = vocab_data['Part_of_speech']
        level = vocab_data['Level']

        # 從篩選按鈕中找到label為part的，回傳這個按鈕的狀態，找不到按鈕則預設為True
        part_cond = next((btn.get_state() for btn in self.toggle_button_list if btn.get_label() == part), True)

        # 從篩選按鈕中找到label為level的，回傳這個按鈕的狀態，找不到按鈕則預設為True
        level_cond = next((btn.get_state() for btn in self.toggle_button_list if btn.get_label() == str(level)), True)

        return part_cond and level_cond

    def generate_row(self, row_index):

        col = 0

        """生成一整排卡片,row_index從0開始"""
        while col < self.cards_per_row and self.current_vocab_index < len(self.vocab_list):
            voc_data = self.vocab_list[self.current_vocab_index]

            passed = self.is_pass_vocab_filter(voc_data)

            if passed:
                voc_id = voc_data['ID']
                x = 400 + col * self.card_width
                y = 380 + row_index * self.card_height
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
            self.text_sound_button_1 = None
            self.text_sound_button_2 = None
        else:
            self.foreground_card = Card(pos=(game.CANVAS_WIDTH/2-400, game.CANVAS_HEIGHT/2), scale=4,id=card_id)
            self.foreground_card_info = Card_Info((game.CANVAS_WIDTH/2+360, 500), 3, card_id)
            self.text_sound_button_1 = Text_Sound_Button(pos=self.foreground_card_info.pos_for_voc_button, scale=0.5, text=self.foreground_card_info.voc)
            self.text_sound_button_2 = Text_Sound_Button(pos=self.foreground_card_info.pos_for_sentence, scale=0.5, text=self.foreground_card_info.sentence)

    def update_background_cards(self):
        # 進行排序(先照等級，再照耐久)
        self.vocab_list = []
        for card in self.user_db.get_card_info(game.USER_ID):
            if card['durability'] <= 0:
                continue
            voc_dic = self.voc_db.find_vocabulary(id=card['voc_id'])[0]
            voc_dic['durability'] = int(card['durability'])
            self.vocab_list += [voc_dic]

        self.vocab_list = sorted(self.vocab_list, key=lambda x: x["durability"])
        
        self.reset_background_cards()
        for card in self.background_cards:
            card.update_image()

    # override
    def handle_event(self):   
        for e in game.event_list:
            if e.type == Event_Manager.EVENT_ANEWDAY:
                self.update_background_cards()
                
                
        self.confirm_quit_object.handle_event()

        # 有放大卡，檢查點擊位置，不在卡片上就關掉
        if self.foreground_card:
            self.foreground_card.handle_event()
            self.text_sound_button_1.handle_event()
            self.text_sound_button_2.handle_event()
            for event in game.event_list:
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    scaled_pos = (mx * game.MOUSE_SCALE, my * game.MOUSE_SCALE)
                    if self.foreground_card and self.foreground_card_info and not self.foreground_card.rect.collidepoint(scaled_pos) and not self.foreground_card_info.rect.collidepoint(scaled_pos):
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
        self.confirm_quit_object.update()
        self.background_cards.update()
       
        for card in self.background_cards:
            card.rect.centery = card.ori_y + self.scroll_offset
            card.hit_box = card.rect.copy()

        self.ui_sprites.update()
        if self.foreground_card:
            self.text_sound_button_1.update()
            self.text_sound_button_2.update()
            self.foreground_card.update()
            self.foreground_card_info.update()

        if self.background_cards:
            max_original_y = max(card.ori_y for card in self.background_cards)
            if max_original_y + self.scroll_offset < game.CANVAS_HEIGHT:
                self.total_rows += 1
                self.generate_row(self.total_rows - 1)

    # override
    def render(self):
        owned_cards = len(self.user_db.get_card_info(user_id = 1))
        total_cards = len(self.voc_db.get_all())
        first_card_text = f"已擁有/總卡牌數：{owned_cards}/{total_cards}"

        not_hidden_cards = len(self.user_db.get_card_durability_below(user_id = 1, durability = 0))
        second_card_text = f"隱藏卡牌數：{not_hidden_cards}"

        Font_Manager.draw_text(game.canvas, "卡牌庫", 70, game.CANVAS_WIDTH/2, 100)
        Font_Manager.draw_text(game.canvas, first_card_text, 30, game.CANVAS_WIDTH/2 -500 , 70)
        Font_Manager.draw_text(game.canvas, second_card_text, 30, game.CANVAS_WIDTH/2 -500 , 130)

        self.ui_sprites.draw(game.canvas)

        self.render_background()
        self.render_foreground()

        self.confirm_quit_object.render()
        
    def render_background(self):
        # 進行卡片畫面截斷
        background_cards_list = []
        for card in self.background_cards:
            # 卡片在顯示區域中
            if card.rect.bottom > self.background_top and card.rect.top < self.background_bottom:

                visible_rect = card.rect.clip(pg.Rect(
                0, self.background_top,
                game.CANVAS_WIDTH, self.background_bottom - self.background_top
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
        game.canvas.blits([(dark_overlay, (0, 0)), (self.foreground_card.image, self.foreground_card.rect), (self.foreground_card_info.image, self.foreground_card_info.rect), (self.text_sound_button_1.image, self.text_sound_button_1.rect), (self.text_sound_button_2.image, self.text_sound_button_2.rect)])  # 把暗幕、放大卡片、卡片資訊畫上去
