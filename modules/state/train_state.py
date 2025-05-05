import pygame as pg
import random
import game
from modules.database import VocabularyDB
from .state import State
from ..object import Text_Button
from ..object import Card
from ..object import Group
from ..object import Deck, Hand
from ..manager import Font_Manager
from ..manager import Image_Manager

class Train_State(State):
    ########################################################################
    #.............................初始化設定...............................#
    #######################################################################
    def __init__(self):
        from ..state import Menu_State
        self.all_sprites = Group()
        self.check_group = Group()
        #文字設定
        self.current_title_text = "Train Room!"
        self.current_question_text = ""
        self.current_result_text = ""
        self.current_translation_text = ""
        #flag設定
        self.back_to_menu = False
        self.result_shown = False
        self.IsAnswering = False
        self.is_drawing_cards = False
        #抽牌設定
        self.card_draw_start_time = 0
        self.card_draw_interval = 500  # 毫秒
        self.deck = None
        self.hand = None
        self.pending_cards = []
        #數值設定
        self.score = 0 #分數
        self.question_num = 6 #題數
        self.question_count = 0 #目前題數
        self.hand_card_num = 6 #手牌數量
        self.hand_card_count = 0 #目前手牌數量
        #按鈕設定
        menu_button = Text_Button(pos=(game.CANVAS_WIDTH - 120, game.CANVAS_HEIGHT - 80), scale=1, text='MENU', font_size=70)
        menu_button.setClick(lambda: game.change_state(Menu_State()))
        self.all_sprites.add(menu_button)
        self.difficulty_select()
    
    ########################################################################
    #.........................設定返回主畫面按鈕............................#
    #######################################################################
    def setMenuButton(self):
        menu_button = Text_Button(pos=(100,100), scale=1, text='Menu', font_size=40)
        menu_button.setClick(lambda:self.check_go_to_menu())
        self.all_sprites.add(menu_button)
        
    def check_go_to_menu(self):
        self.current_result_text= "Are you sure to go back to menu?"
        self.IsAnswering = False
        self.back_to_menu = True
        self.checkbtnY = Text_Button(pos=(game.CANVAS_WIDTH/2-200, game.CANVAS_HEIGHT/2), scale=1, text="Yes", font_size=70)
        self.checkbtnY.setClick(lambda: self.go_to_menu())
        self.checkbtnN = Text_Button(pos=(game.CANVAS_WIDTH/2+200, game.CANVAS_HEIGHT/2), scale=1, text="No", font_size=70)
        self.checkbtnN.setClick(lambda : self.cancel_go_to_menu())
        self.check_group.add(self.checkbtnY, self.checkbtnN)
        self.all_sprites.add(self.checkbtnY, self.checkbtnN)
        for sprite in self.all_sprites:
            if sprite not in (self.checkbtnY, self.checkbtnN):
                sprite.active = False
        
    def cancel_go_to_menu(self):
        self.back_to_menu = False
        self.IsAnswering = True
        self.current_result_text = ""
        self.all_sprites.remove(self.checkbtnY)
        self.all_sprites.remove(self.checkbtnN)
        self.check_group.remove(self.checkbtnY)
        self.check_group.remove(self.checkbtnN)
        
    def go_to_menu(self):
        game.background_color = (30,30,30)
        from .menu_state import Menu_State
        game.change_state(Menu_State())
    
    ########################################################################
    #...........................難度題型選擇................................#
    ########################################################################
    #選擇難度
    def difficulty_select(self):
        from ..state import Menu_State
        self.all_sprites.empty()
        self.setMenuButton()
        self.difficulty_buttons = []
        self.level = 0
        for i in range(3):
            btn = Text_Button(pos=(game.CANVAS_WIDTH/2, 400 + i*200), scale=1, text="LEVEL"+str(i+1), font_size=30)
            btn.setClick(lambda level=i+1: self.question_type_select(level))
            self.difficulty_buttons.append(btn)
            self.all_sprites.add(btn)
    
    #選擇題型
    #0:單字中翻英 1:單字英翻中 2:例句填空
    def question_type_select(self, level):
        from ..state import Menu_State
        self.all_sprites.empty()
        self.setMenuButton()
        self.difficulty_buttons = []
        self.question_type = 0
        btn1 = Text_Button(pos=(game.CANVAS_WIDTH/2, 400), scale=1.5, text="單字中翻英", font_size=28)
        btn1.setClick(lambda type=0: self.start_game(type, level))
        self.difficulty_buttons.append(btn1)
        self.all_sprites.add(btn1)

        btn2 = Text_Button(pos=(game.CANVAS_WIDTH/2, 600), scale=1.5, text="單字英翻中", font_size=28)
        btn2.setClick(lambda type=1: self.start_game(type, level))
        self.difficulty_buttons.append(btn2)
        self.all_sprites.add(btn2)

        btn3 = Text_Button(pos=(game.CANVAS_WIDTH/2, 800), scale=1.5, text="例句填空", font_size=28)
        btn3.setClick(lambda type=2: self.start_game(type, level))
        self.difficulty_buttons.append(btn3)
        self.all_sprites.add(btn3)

    ########################################################################
    #.............................載入題目..................................#
    ########################################################################
    def load_question(self, type, level):
        self.result_shown = False

        if self.question_count < self.question_num:
            print('load question')

            # 設定抽牌階段
            self.question_count += 1
            self.all_sprites.empty()
            self.setMenuButton()
            self.draw_cards_from_deck()
        else:
            print('end')
            self.hand.deactivate()
            self.show_result()
    
    #題目顯示
    def setup_question_display(self):
        self.IsAnswering = True
        self.hand.activate()
        self.current_title_text = "Question " + str(self.question_count)
        self.answer_data = self.hand.get_card_at(random.randint(0, self.hand.cards_count() - 1)).data
        self.answer_history.append(self.answer_data)

        if self.question_type == 0:
            self.current_question_text = self.answer_data['Translation']
        elif self.question_type == 1:
            self.current_question_text = self.answer_data['Vocabulary']
        elif self.question_type == 2:
            self.question = self.db.get_example_sentences(voc_id=self.answer_data['ID'])[0]
            sentence = self.question['sentence']
            self.current_question_text = sentence.replace(self.answer_data, "_____")
            self.question_history.append(self.question)
        
    ########################################################################
    #.............................答案檢查..................................#
    ########################################################################
    def check_answer(self, type, selected_card_data:dict):
        if self.result_shown or not self.IsAnswering:
            return
        
        self.selected_history.append(selected_card_data['Vocabulary'])
        self.IsAnswering = False
        self.hand.deactivate()
        self.hand.remove_card_by_ID(selected_card_data['ID'])

        if selected_card_data['ID'] == self.answer_data['ID']:
            # self.voc_list.remove(selected_card.data)
            self.score += 1
            self.current_result_text = "Correct!"
        else:
            self.current_result_text = f"Wrong! Correct Answer: {self.answer_data['Vocabulary']}"
            # TODO: Card移動到棄牌堆
            self.hand.remove_card_by_ID(self.answer_data['ID'])

        self.result_shown = True
        if type == 2:
            self.current_translation_text = f"Translation: {self.question['translation']}"
        next_button = Text_Button(
            pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT-480),
            scale=1,
            text='Next',
            font_size=70
        )
        next_button.setClick(lambda: self.load_question(type, self.level))
        self.all_sprites.add(next_button)
    
    #顯示結果
    def show_result(self):
        from ..state import Menu_State
        self.all_sprites.empty()
        self.setMenuButton()
        self.current_title_text = "Result"
        self.current_question_text = ""
        self.current_translation_text = ""
        self.current_result_text = f"Your score: {self.score}/{self.question_num}"
        self.result_shown = True
        
        #在terminal顯示歷史紀錄
        print("\n================= Quiz Summary =================")
        for i in range(self.question_num):
            print(f"\n[Question {i+1}]")
            
            # 題目
            if self.question_type == 0:
                # prompt = next(c['Translation'] for c in self.chose_history[i] if c['Vocabulary'] == self.answer_history[i])
                prompt = self.answer_history[i]['Translation']
            elif self.question_type == 1:
                prompt = self.answer_history[i]
            elif self.question_type == 2:
                prompt = self.question_history[i]['sentence'].replace(self.answer_history[i], '_____')
            
            print(f"  - Prompt         : {prompt}")
            print(f"  - Correct Answer : {self.answer_history[i]}")
            print(f"  - Your Answer    : {self.selected_history[i]}")
            result = '✓ Correct' if self.selected_history[i] == self.answer_history[i] else '✗ Wrong'
            print(f"  - Result         : {result}")
        print("================================================\n")


    #遊戲開始
    def start_game(self, type, level):
        self.all_sprites.empty()
        self.setMenuButton()

        from modules.database import VocabularyDB
        self.question_history = []
        self.answer_history = []    # 出現過的正解
        self.selected_history = []  # 選過的Vocabulary
        self.level = level
        self.db = VocabularyDB()
        self.voc_list = self.db.find_vocabulary(level=level)
        self.chose_history = []  
        self.question_type = type
        self.level = level
        self.deck = Deck((game.CANVAS_WIDTH - 200, 200), random.sample(self.voc_list, self.question_num * 2 + self.hand_card_num))
        self.hand = Hand((game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT - 200), game.CANVAS_WIDTH // 1.5, self.hand_card_num)

        self.load_question(type, level)

    #####################################################################
    #..............................工具.................................#
    #####################################################################
    #換行顯示文字
    def draw_wrapped_text(self, surface: pg.Surface, text: str, font: pg.font.Font, color: tuple, x: int, y: int, max_width: int, line_spacing: int = 10) -> None:
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
    

    #########################################################################
    #.............................更新與事件處理.............................#
    #########################################################################

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
            self.setup_question_display()  # 沒牌可抽就直接下一題
            return
        self.hand.deactivate()
        now = pg.time.get_ticks()
        if now - self.card_draw_start_time >= self.card_draw_interval:
            # 等最後一張跑完再繼續
            if not self.hand.first_empty_slot_pos():
                self.is_drawing_cards = False
                self.setup_question_display()  # 抽滿了就下一題
                return
            card = self.deck.draw_a_card()
            card.can_press = True
            card.moveTo(self.hand.first_empty_slot_pos(), self.card_draw_interval)
            card.setClick(lambda: self.check_answer(self.question_type, card.data))
            self.hand.add_card(card)
            self.card_draw_start_time = now
            self.chose_history.append(card.data)

    def handle_event(self):
        self.all_sprites.handle_event()
        if self.deck != None:
            self.deck.handle_event()
        if self.hand != None:
            self.hand.handle_event()

    def update(self):
        self.draw_cards_from_deck_animation()
        self.all_sprites.update()
        if self.deck != None:
            self.deck.update()
        if self.hand != None:
            self.hand.update()

    def render(self):
        Font_Manager.draw_text(game.canvas, self.current_title_text, 70, game.CANVAS_WIDTH/2, 100)
        if self.current_question_text:
            font = pg.font.Font("res\\font\\SWEISANSCJKTC-REGULAR.TTF", 60)
            self.draw_wrapped_text(game.canvas, self.current_question_text, font, (255, 255, 255), 100, 180, game.CANVAS_WIDTH - 200)
        if self.result_shown:
            Font_Manager.draw_text(game.canvas, self.current_result_text, 50, game.CANVAS_WIDTH//2, 350)
            Font_Manager.draw_text(game.canvas, self.current_translation_text, 50, game.CANVAS_WIDTH//2, 450)
        self.all_sprites.draw(game.canvas)

        if self.deck:
            self.deck.render()

        if self.hand:
            self.hand.draw(game.canvas)

        if self.back_to_menu:
            dark_overlay = pg.Surface((game.CANVAS_WIDTH, game.CANVAS_HEIGHT), flags=pg.SRCALPHA) #黑幕頁面
            dark_overlay.fill((0, 0, 0, 180))  # RGBA，最後一個值是透明度（0~255）
            game.canvas.blit(dark_overlay, (0, 0))  # 把暗幕畫上去
            Font_Manager.draw_text(game.canvas, self.current_result_text, 50, game.CANVAS_WIDTH//2, 350)
            self.check_group.draw(game.canvas)
