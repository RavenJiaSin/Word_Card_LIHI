from datetime import datetime
import math
import re
import pygame as pg
import random
import game
from modules.manager.sfx_manager import SFX_Manager
from .state import State
from ..object import Object, Text_Button
from ..object import Group
from ..object import Confirm_Quit_Object, Card
from ..object import Deck, Hand
from ..manager import Font_Manager, Image_Manager
from ..manager import Train_Enum
from ..manager import Event_Manager
from modules.database import VocabularyDB
from modules.database.userDBconnect import UserDB


class Train_Play_State(State):
    """練功坊答題狀態。繼承自`State`。
    
    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
    
    """

    def __init__(self, level:int, mode:int):

        # === 變數 ===
        # 文字設定
        self.current_question_text = ""

        # 數值設定
        self.card_scale = 1.5      #卡牌大小
        self.score = 0             #分數
        self.question_num = 5      #題數
        self.question_count = 0    #目前題數
        self.hand_card_num = 6     #手牌數量
        self.current_card_num = 0  #目前手牌數量
        # 動畫
        self.card_draw_start_time = 0
        self.card_play_start_time = 0
        self.card_draw_interval = 50  # 毫秒，抽牌時間
        self.card_play_interval = 500  # 毫秒，出卡時間

        # flags
        self.showing_result = False
        self.showing_correct = False
        self.showing_wrong = False
        self.is_drawing_cards = False
        self.is_playing_a_card = False

        # 題目與答題記錄，以 card.__data 的格式存放
        self.history = dict({Train_Enum.QUESTION: [], 
                             Train_Enum.ANSWER: [], 
                             Train_Enum.SELECTED: []})
        self.level = level
        self.db = VocabularyDB()
        self.voc_list = self.db.find_vocabulary(level=level)
        self.mode = mode

        self.user_id = 1  
        self.user_db = UserDB()

        # === UI ===
        self.all_sprites = Group()
        
        # 更新遊玩次數
        play_count = self.user_db.get_user_info(user_id=self.user_id, column="total_time")[0]["total_time"]+1
        self.user_db.update_user_info(user_id= self.user_id, total_time = play_count)
        
        # 建立牌堆與手牌
        self.create_deck()
        self.hand = Hand((game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT - 200), self.hand_card_num * 100, self.hand_card_num)
        
        # 建立返回首頁按鈕
        from . import Menu_State
        self.confirm_quit_object = Confirm_Quit_Object(lambda:game.change_state(Menu_State()))
        menu_button = Text_Button(pos=(100, 100), text='首頁')
        menu_button.setClick(lambda: self.confirm_quit_object.set_show(True))
        self.all_sprites.add(menu_button)

        # 對/錯 卡牌提示背景
        self.correct_indicator = Object(scale=self.card_scale * 1.12, img=Image_Manager.get('card_green_glow'))
        self.wrong_indicator = Object(scale=self.card_scale * 1.12, img=Image_Manager.get('card_red_glow'))

        # 下一題
        self.next_button = Text_Button(
            pos=(game.CANVAS_WIDTH // 2 + 250, game.CANVAS_HEIGHT - 450),
            text='Next'
        )
        self.next_button.setClick(self.next_btn_func)

        self.next_question()

    ############ 出題 #############

    def create_deck(self):
        if 1 <= self.level <= 6:
            self.create_deck_by_level()
        elif self.level == Train_Enum.AUTO:
            self.create_deck_by_auto()
        elif self.level == Train_Enum.DAILY:
            self.create_deck_by_daily()
        
    def create_deck_by_level(self):
        '''
        按當前level創造卡牌堆
        優先放入耐久值過低的使用者卡牌以供複習
        '''
        deck_card_num = self.question_num*2 + self.hand_card_num
        
        cards_need_review = self.user_db.get_card_durability_below(user_id = 1, durability = 40)
        card_to_review = []
        for voc in cards_need_review:
            card_info = self.db.find_vocabulary(id=voc['voc_id'])[0]
            if card_info['Level'] == self.level:
                card_to_review.append(card_info)
        
        card_to_review_num = deck_card_num*4  # 期望值，卡堆中最多有80%是待複習的卡
        card_to_review_num = min(card_to_review_num, len(card_to_review))  # 避免隨機抽樣數大於樣本空間
        
        card_to_review = random.sample(card_to_review, card_to_review_num)
        new_cards = random.sample(self.voc_list, deck_card_num)

        cards_to_select = new_cards + card_to_review
        cards_to_select = random.sample(cards_to_select, deck_card_num)
        self.deck = Deck((game.CANVAS_WIDTH - 200, 200), self.card_scale, cards_to_select, self.mode)

    def create_deck_by_auto(self): # TODO: copy pasted code
        all_voc = self.db.get_all()
        user_voc = self.user_db.get_card_info(user_id=game.USER_ID)

        # 計算總共點數，一張 Level n 的卡 = n 點
        total_point = 0
        for voc in all_voc:
            total_point += voc['Level']

        # 計算使用者點數
        user_point = 0
        for voc in user_voc:
            user_point += self.db.find_vocabulary(id=voc['voc_id'])[0]['Level']
        # print(user_point)

        # 計算使用者等級，將卡牌庫總點數分成6個區間 (1~6)
        point_per_level = total_point // 6
        user_level = user_point // point_per_level + 1

        # 獲取使用者未擁有的卡牌
        all_voc_id = {voc['ID'] for voc in all_voc}
        user_voc_id = {voc['voc_id'] for voc in user_voc}

        have_not_gain_voc_id = all_voc_id - user_voc_id
        
        # 取得未擁有的卡牌，並按level分類
        draw_from_voc = [[] for i in range(6)]
        for i in range(6):
            draw_from_voc[i] = [voc for voc in all_voc if voc['ID'] in have_not_gain_voc_id and voc['Level'] == i+1]

        # 根據使用者等級抽卡
        card_pool = []
        for i in range(1,7):
            # 盡量給接近使用者等級的卡
            level_difference = abs(user_level - i)
            weight = 0
            if level_difference == 0:
                weight = 6
            elif level_difference == 1:
                weight = 1.5
            elif level_difference == 2:
                weight = 0.5
            
            card_pool += random.sample(draw_from_voc[i-1], math.ceil((self.question_num*2 + self.hand_card_num) * weight))
        auto_card = random.sample(card_pool, self.question_num*2 + self.hand_card_num)
        self.deck = Deck((game.CANVAS_WIDTH - 200, 200), self.card_scale, auto_card, self.mode)

    def create_deck_by_daily(self):
        '''
        牌堆全都是每日卡牌
        '''
        self.question_num = len(game.daily_card_ids)
        daily_card = []
        for voc_id in game.daily_card_ids:
            daily_card.append(self.db.find_vocabulary(id=voc_id)[0])
        self.deck = Deck((game.CANVAS_WIDTH - 200, 200), self.card_scale, daily_card, self.mode)

    ########## 題目與作答 ##########

    def next_question(self):
        '''
        發題目
        '''
        if self.question_count < self.question_num:
            self.question_count += 1
            self.draw_cards_from_deck()
        else:
            from . import Train_Result_State
            game.change_state(Train_Result_State(self.level, self.mode,self.history))

    def load_question(self):
        '''
        從手牌中抽一個當題目，並開始作答
        '''
        if self.hand.cards_count() <= 0:
            self.next_question()
            return
        self.hand.activate()
        self.current_title_text = "Question " + str(self.question_count)
        self.answer_data = self.hand.get_a_random_card().get_data()
        self.history[Train_Enum.ANSWER].append(self.answer_data)

        if self.mode == Train_Enum.CHI2ENG:
            self.current_question_text = self.answer_data['Translation']
        elif self.mode == Train_Enum.ENG2CHI:
            self.current_question_text = self.answer_data['Vocabulary']
        elif self.mode == Train_Enum.SENTENCE:
            self.question = self.db.get_example_sentences(voc_id=self.answer_data['ID'])[0]
            sentence = self.question['sentence']
            self.current_question_text = re.sub(fr"\b{self.answer_data['Vocabulary']}\b", '_____', sentence, flags=re.IGNORECASE)            

        self.history[Train_Enum.QUESTION].append(self.current_question_text)

    def check_answer(self):
        selected_card_data = self.__selected_card.get_data()
        self.history[Train_Enum.SELECTED].append(selected_card_data)

        if selected_card_data['ID'] == self.answer_data['ID']:
            # 答對
            SFX_Manager.play('ingame_correct')
            self.score += 1
            self.current_result_text = "Correct!"
            self.__correct_card = self.__selected_card
            self.all_sprites.add(self.correct_indicator, layer=-1)
            self.showing_correct = True

            # user 卡牌庫更新
            voc_id = selected_card_data['ID']
            user_card = self.user_db.get_card_info(voc_id=voc_id)
            if len(user_card) != 0:
                # 使用者已有這卡牌
                user_card = user_card[0]                
                self.user_db.update_card_info(user_id = game.USER_ID,
                                              voc_id = voc_id,
                                              durability = 100,
                                              last_review = datetime.now(),
                                              proficiency = min(user_card['proficiency']+1, 6),  # TODO: 當天重複review到不升級，避免每日卡牌關可刷等
                                              correct_count = user_card['correct_count'] + 1,
                                              )
            else:
                # 獲得新卡牌
                self.user_db.add_card_to_user(user_id=game.USER_ID, voc_id=selected_card_data['ID'])
                self.user_db.update_card_info(user_id = game.USER_ID,
                                              voc_id = voc_id,
                                              durability = 100,
                                              last_review = datetime.now(),
                                              proficiency = 1,
                                              correct_count = 1,
                                              )
        else:
            # 答錯
            SFX_Manager.play('ingame_incorrect')
            self.current_result_text = f"Wrong! Correct Answer: {self.answer_data['Vocabulary']}"
            # TODO: Card移動到棄牌堆
            self.__correct_card = self.hand.get_card_by_ID(self.answer_data['ID'])
            self.__correct_card.setWiggle()
            self.hand.remove_card_by_ID(self.answer_data['ID'])  # 答錯以後，正確卡從手牌中移到桌面，才能顯示在上層
            self.all_sprites.add(self.__correct_card, layer=0)
            self.all_sprites.add(self.correct_indicator, layer=-1)
            self.__wrong_card = self.__selected_card
            self.all_sprites.add(self.wrong_indicator, layer=-1)
            self.showing_correct = True
            self.showing_wrong = True
        
            # 更新使用者卡牌資訊
            selected_card = self.user_db.get_card_info(voc_id=selected_card_data['ID'])
            if len(selected_card) != 0:
                # 使用者已有這卡牌
                selected_card = selected_card[0]                
                self.user_db.update_card_info(user_id = game.USER_ID,
                                              voc_id = selected_card['voc_id'],
                                              wrong_count = selected_card['wrong_count'] + 1,
                                              )
            
            answer_card = self.user_db.get_card_info(voc_id=self.answer_data['ID'])
            if len(answer_card) != 0:
                # 使用者已有這卡牌
                answer_card = answer_card[0]                
                self.user_db.update_card_info(user_id = game.USER_ID,
                                              voc_id = answer_card['voc_id'],
                                              wrong_count = answer_card['wrong_count'] + 1,
                                              )


        self.user_db.log_answer(
            user_id=self.user_id,
            voc_id=self.answer_data['ID'],
            is_correct=(selected_card_data['ID'] == self.answer_data['ID']))

        self.showing_result = True
        # if self.mode == self.ENG2CHI:
        #     self.current_translation_text = f"Translation: {self.question['translation']}"
        
        self.all_sprites.add(self.next_button)
        # 記錄答題結果到 answer_log


    def next_btn_func(self):
        if self.showing_wrong:
            self.wrong_indicator.kill()
            self.showing_wrong = False
        if self.showing_correct:
            self.correct_indicator.kill()
            self.showing_correct = False
        self.__selected_card.kill()
        self.__correct_card.kill()
        self.showing_result = False
        self.next_question()
        self.next_button.kill()

    ########## 動畫 ##########

    def draw_cards_from_deck(self):
        self.is_drawing_cards = True
        self.card_draw_start_time = pg.time.get_ticks()

    def draw_cards_from_deck_animation(self):
        '''
        做動畫並控制題目載入
        '''
        if not self.is_drawing_cards: 
            return
        if self.hand == None or self.deck == None: 
            self.is_drawing_cards = False
            return
        if self.deck.is_empty():
            self.is_drawing_cards = False
            self.load_question()  # 沒牌可抽就直接下一題
            return
        now = pg.time.get_ticks()
        if now - self.card_draw_start_time >= self.card_draw_interval:
            # 等最後一張跑完再繼續
            if not self.hand.first_empty_slot_pos():
                self.is_drawing_cards = False
                self.load_question()  # 抽滿了就下一題
                return
            card = self.deck.draw_a_card()
            card.moveTo((200, 500), self.card_draw_interval * 5, False)
            endPos = self.hand.first_empty_slot_pos()
            card.moveTo(endPos, self.card_draw_interval * 5, False)
            card.moveTo(endPos, 0, True) # 只為了動hit_box
            card.setClick(lambda: self.play_a_card_from_hand(card))
            self.hand.add_card(card)
            self.hand.deactivate()
            self.card_draw_start_time = now

    def play_a_card_from_hand(self, card:Card):
        self.is_playing_a_card = True
        card.moveTo((game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT // 2), self.card_play_interval, True)
        self.__selected_card = card
        self.hand.deactivate()
        self.hand.remove_card_by_ID(card.get_data()['ID'])
        self.all_sprites.add(card)
        self.card_play_start_time = pg.time.get_ticks()
 
    def play_a_card_from_hand_animation(self):
        '''
        等動畫結束並接著對答案
        '''
        if not self.is_playing_a_card:
            return
        now = pg.time.get_ticks()
        if now - self.card_play_start_time > self.card_play_interval:
            self.is_playing_a_card = False
            pg.event.post(pg.event.Event(Event_Manager.EVENT_SHAKE))
            self.__selected_card.transform(scale=1)
            self.check_answer()

    ########## 工具 ##########

    #換行顯示文字
    def draw_wrapped_text(self, surface:pg.Surface, text:str, font:pg.font.Font, color:tuple, x:int, y:int, max_width:int, line_spacing:int = 10) -> None:
        words = text.split(' ')
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            if font.size(test_line)[0] <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)
        for i, line in enumerate(lines):
            rendered_line = font.render(line.strip(), True, color)
            surface.blit(rendered_line, (x, y + i * (font.get_linesize() + line_spacing)))

    ########## 事件處理與更新 ##########

    # override
    def handle_event(self):
        self.confirm_quit_object.handle_event()
        self.all_sprites.handle_event()
        if self.deck != None:
            self.deck.handle_event()
        if self.hand != None:
            self.hand.handle_event()

    # override
    def update(self):
        self.confirm_quit_object.update()
        self.draw_cards_from_deck_animation()
        self.play_a_card_from_hand_animation()
        if self.deck != None:
            self.deck.update()
        if self.hand != None:
            self.hand.update()
        if self.showing_correct:
            self.correct_indicator.x = self.__correct_card.x-1 # 不知道為什麼這樣比較對齊
            self.correct_indicator.y = self.__correct_card.y-1
        if self.showing_wrong:
            self.wrong_indicator.x = self.__wrong_card.x-1
            self.wrong_indicator.y = self.__wrong_card.y-1
        self.all_sprites.update()

    # override
    def render(self):
        # 標題
        Font_Manager.draw_text(game.canvas, "練功坊", 70, game.CANVAS_WIDTH/2, 100)
        # 題目
        if self.current_question_text:
            font = pg.font.Font("res\\font\\SWEISANSCJKTC-REGULAR.TTF", 60)
            self.draw_wrapped_text(game.canvas, self.current_question_text, font, (255, 255, 255), 200, 200, game.CANVAS_WIDTH - 500)
        # 卡堆
        if self.deck != None:
            self.deck.render()
        # 手牌
        if self.hand != None:
            self.hand.render()
        # 答案
        if self.showing_result:
            result_lines = self.current_result_text.split('\n')
            for idx, line in enumerate(result_lines):
                Font_Manager.draw_text(game.canvas, line, 50, game.CANVAS_WIDTH//2, 300 + idx * 60)

        self.all_sprites.draw(game.canvas)
        self.confirm_quit_object.render()
