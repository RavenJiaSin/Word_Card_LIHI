import pygame as pg
import random
import game
from .state import State
from ..object import Text_Button
from ..object import Group
from ..object import Confirm_Quit_Object
from ..object import Deck, Hand
from ..manager import Font_Manager
from ..manager import Train_Enum
from modules.database import VocabularyDB



class Train_Play_State(State):
    """練功坊答題狀態。繼承自`State`。

    在結構子中，創建`all_sprites`(sprite.Group)，以管理所有首頁會出現的`Object`物件，其他頁面都可以參照這個做法。

    覆寫`update()`時，呼叫`all_sprites.update()`，此時會呼叫我們在`Object`中覆寫的`update()`。

    覆寫`render()`時，呼叫`game.draw_text()`，可以寫文字，並且呼叫`all_sprites.draw()`，此時會根據Object中的rect的資訊，畫出Object中的image。

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
    
    """

    def __init__(self, level:int, mode:int):

        # === 變數 ===
        self.showing_result = False
        # 文字設定
        self.current_question_text = ""

        # 數值設定
        self.score = 0             #分數
        self.question_num = 2      #題數
        self.question_count = 0    #目前題數
        self.hand_card_num = 6     #手牌數量
        self.current_card_num = 0  #目前手牌數量
        # 動畫
        self.card_draw_start_time = 0
        self.card_draw_interval = 350  # 毫秒

        # 題目與答題記錄，以 card.__data 的格式存放
        self.history = dict({Train_Enum.QUESTION: [], 
                             Train_Enum.ANSWER: [], 
                             Train_Enum.SELECTED: []})
        self.level = level
        self.db = VocabularyDB()
        self.voc_list = self.db.find_vocabulary(level=level)
        self.mode = mode
        self.deck = Deck((game.CANVAS_WIDTH - 200, 200), random.sample(self.voc_list, self.question_num * 2 + self.hand_card_num))
        self.hand = Hand((game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT - 200), game.CANVAS_WIDTH // 1.5, self.hand_card_num)

        # === UI ===
        self.all_sprites = Group()
        
        # 建立返回首頁按鈕
        from . import Menu_State
        self.confirm_quit_object = Confirm_Quit_Object(lambda:game.change_state(Menu_State()))
        menu_button = Text_Button(pos=(100, 100), text='首頁')
        menu_button.setClick(lambda: self.confirm_quit_object.set_show(True))
        self.all_sprites.add(menu_button)

        # 下一題
        self.next_button = Text_Button(
            pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT-480),
            text='Next'
        )
        self.next_button.setClick(self.next_btn_func)

        self.next_question()

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
        self.hand.activate()
        self.current_title_text = "Question " + str(self.question_count)
        self.answer_data = self.hand.get_card_at(random.randint(0, self.hand.cards_count() - 1)).get_data()
        self.history[Train_Enum.ANSWER].append(self.answer_data)

        if self.mode == Train_Enum.CHI2ENG:
            self.current_question_text = self.answer_data['Translation']
        elif self.mode == Train_Enum.ENG2CHI:
            self.current_question_text = self.answer_data['Vocabulary']
        elif self.mode == Train_Enum.SENTENCE:
            self.question = self.db.get_example_sentences(voc_id=self.answer_data['ID'])[0]
            sentence = self.question['sentence']
            self.current_question_text = sentence.replace(self.answer_data['Vocabulary'], "_____")

        self.history[Train_Enum.QUESTION].append(self.current_question_text)

    def check_answer(self, selected_card_data:dict):

        self.hand.deactivate()
        self.history[Train_Enum.SELECTED].append(selected_card_data)
        self.hand.remove_card_by_ID(selected_card_data['ID'])

        if selected_card_data['ID'] == self.answer_data['ID']:
            # self.voc_list.remove(selected_card.data)
            self.score += 1
            self.current_result_text = "Correct!"
        else:
            self.current_result_text = f"Wrong! Correct Answer: {self.answer_data['Vocabulary']}"
            # TODO: Card移動到棄牌堆
            self.hand.remove_card_by_ID(self.answer_data['ID'])

        self.showing_result = True
        # if self.mode == self.ENG2CHI:
        #     self.current_translation_text = f"Translation: {self.question['translation']}"
        
        self.all_sprites.add(self.next_button)

    def next_btn_func(self):
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
        self.hand.deactivate()
        now = pg.time.get_ticks()
        if now - self.card_draw_start_time >= self.card_draw_interval:
            # 等最後一張跑完再繼續
            if not self.hand.first_empty_slot_pos():
                self.is_drawing_cards = False
                self.load_question()  # 抽滿了就下一題
                return
            card = self.deck.draw_a_card()
            card.can_press = True
            card.moveTo(self.hand.first_empty_slot_pos(), self.card_draw_interval)
            card.setClick(lambda: self.check_answer(card.get_data()))
            self.hand.add_card(card)
            self.card_draw_start_time = now

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
        if self.deck != None:
            self.deck.handle_event()
        if self.hand != None:
            self.hand.handle_event()
        self.all_sprites.handle_event()

    # override
    def update(self):
        self.confirm_quit_object.update()
        self.draw_cards_from_deck_animation()
        if self.deck != None:
            self.deck.update()
        if self.hand != None:
            self.hand.update()
        self.all_sprites.update()

    # override
    def render(self):
        # 標題
        Font_Manager.draw_text(game.canvas, "練功坊", 70, game.CANVAS_WIDTH/2, 100)
        # 題目
        if self.current_question_text:
            font = pg.font.Font("res\\font\\SWEISANSCJKTC-REGULAR.TTF", 60)
            self.draw_wrapped_text(game.canvas, self.current_question_text, font, (255, 255, 255), 200, 180, game.CANVAS_WIDTH - 200)
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
