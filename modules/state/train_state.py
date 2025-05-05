import pygame as pg
import random
import game
from modules.database import VocabularyDB
from .state import State
from ..object import Text_Button
from ..object import Card
from ..object import Group
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
        self.back_to_menu_text= ""
        #flag設定
        self.back_to_menu = False
        self.result_shown = False
        self.IsAnswering = False
        self.is_drawing_cards = False
        self.is_reviewing = False
        self.selected_card_index = None  # 目前選取的卡片編號
        self.confirm_button = None       # 確認按鈕參考

        #抽牌設定
        self.card_draw_start_time = 0
        self.card_draw_interval = 120  # 毫秒
        self.pending_cards = []
        #數值設定
        self.score = 0 #分數
        self.question_num = 6 #題數
        self.question_count = 0 #目前題數
        self.hand_card_num = 4 #手牌數量
        self.current_card_num = 0 #目前手牌數量
        self.review_index = 0 #回顧題目索引
        #按鈕設定
        menu_button = Text_Button(pos=(game.CANVAS_WIDTH - 120, game.CANVAS_HEIGHT - 80), text='MENU')
        menu_button.setClick(lambda: game.change_state(Menu_State()))
        self.all_sprites.add(menu_button)
                
        #開始執行
        self.difficulty_select()
    
    ########################################################################
    #.........................設定返回主畫面按鈕............................#
    #######################################################################
    def setMenuButton(self):
        menu_button = Text_Button(pos=(100,100), text='首頁')
        menu_button.setClick(lambda:self.check_go_to_menu())
        self.all_sprites.add(menu_button)
        
    def check_go_to_menu(self):
        self.back_to_menu_text= "Are you sure to go back to menu?"
        self.IsAnswering = False
        self.back_to_menu = True
        self.checkbtnY = Text_Button(pos=(game.CANVAS_WIDTH/2-200, game.CANVAS_HEIGHT/2), text="Yes")
        self.checkbtnY.setClick(lambda: self.go_to_menu())
        self.checkbtnN = Text_Button(pos=(game.CANVAS_WIDTH/2+200, game.CANVAS_HEIGHT/2), text="No")
        self.checkbtnN.setClick(lambda : self.cancel_go_to_menu())
        self.check_group.add(self.checkbtnY, self.checkbtnN)
        self.all_sprites.add(self.checkbtnY, self.checkbtnN)
        for sprite in self.all_sprites:
            if sprite not in (self.checkbtnY, self.checkbtnN):
                sprite.active = False
        
    def cancel_go_to_menu(self):
        self.back_to_menu = False
        self.IsAnswering = True
        self.back_to_menu_text = ""
        self.all_sprites.remove(self.checkbtnY)
        self.all_sprites.remove(self.checkbtnN)
        self.check_group.remove(self.checkbtnY)
        self.check_group.remove(self.checkbtnN)
        
    def go_to_menu(self):
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
        for i in range(6):
            btn = Text_Button(pos=(game.CANVAS_WIDTH/2-300+600*(i%2), 400 + i//2*200), text="LEVEL"+str(i+1))
            btn.setClick(lambda level=i+1: self.question_type_select(level))
            self.difficulty_buttons.append(btn)
            self.all_sprites.add(btn)
    
    #選擇題型
    #0:單字中翻英 1:單字英翻中 2:例句填空
    def question_type_select(self, level):
        if not self.back_to_menu:
            from ..state import Menu_State
            self.all_sprites.empty()
            self.setMenuButton()
            self.difficulty_buttons = []
            self.question_type = 0
            btn1 = Text_Button(pos=(game.CANVAS_WIDTH/2, 400), text="單字中翻英")
            btn1.setClick(lambda type=0: self.start_game(type, level))
            self.difficulty_buttons.append(btn1)
            self.all_sprites.add(btn1)

            btn2 = Text_Button(pos=(game.CANVAS_WIDTH/2, 600), text="單字英翻中")
            btn2.setClick(lambda type=1: self.start_game(type, level))
            self.difficulty_buttons.append(btn2)
            self.all_sprites.add(btn2)

            btn3 = Text_Button(pos=(game.CANVAS_WIDTH/2, 800), text="例句填空", font_size=70)
            btn3.setClick(lambda type=2: self.start_game(type, level))
            self.difficulty_buttons.append(btn3)
            self.all_sprites.add(btn3)

    ########################################################################
    #.............................載入題目..................................#
    ########################################################################
    def load_question(self, qtype, level):
        if self.question_count < self.question_num:
            if self.current_card_num == 0:
                from modules.database import VocabularyDB
                self.question_history = []
                self.card_history = []
                self.answer_history = []
                self.selected_history = []
                self.level = level
                self.db = VocabularyDB()
                self.voc_list = self.db.find_vocabulary(level=level)
                self.choice = []
                self.choice_history = []

            # 設定抽牌階段
            self.question_count += 1
            self.all_sprites.empty()
            self.setMenuButton()
            for sprite in list(self.all_sprites):
                if isinstance(sprite, Card):
                    self.all_sprites.remove(sprite)

            # 重新將還在手上的卡片畫出來
            for idx, card_data in enumerate(self.choice):
                card = Card(
                    pos=(game.CANVAS_WIDTH // 2 - 90 * self.hand_card_num + 250 * idx, 1000),
                    scale=2,
                    id=card_data['Vocabulary'],
                    show_eng=(self.question_type != 1),  
                    show_chi=(self.question_type != 0)  
                )
                card.setClick(lambda i=idx: self.play_card(self.question_type, i))
                self.all_sprites.add(card)
                
            available_cards = [v for v in self.voc_list if v not in self.choice]
            draw_count = self.hand_card_num - self.current_card_num
            draw_count = min(draw_count, len(available_cards))
            self.pending_cards = random.sample(available_cards, draw_count)
            self.card_draw_start_time = pg.time.get_ticks()
            self.is_drawing_cards = True
        else:
            self.show_result()
    
    #題目顯示
    def setup_question_display(self):
        self.result_shown = False
        self.IsAnswering = True
        self.current_title_text = "Question " + str(self.question_count)
        self.answer_index = random.randint(0, self.current_card_num - 1)
        self.answer = self.choice[self.answer_index]['Vocabulary']
        self.answer_history.append(self.answer)
        self.choice_history.append(self.choice[:])

        if self.question_type == 0:
            self.current_question_text = self.choice[self.answer_index]['Translation']
        elif self.question_type == 1:
            self.current_question_text = self.choice[self.answer_index]['Vocabulary']
        elif self.question_type == 2:
            example_sentences = self.db.get_example_sentences(voc_id=self.choice[self.answer_index]['ID'])
            if example_sentences:
                self.question = example_sentences[0]
                sentence = self.question.get('sentence', '')
                self.current_question_text = sentence.replace(self.answer, "_____")
                self.question_history.append(self.question)
            else:
                self.question = None
                self.current_question_text = "[No example sentence found]"
                self.question_history.append({"sentence": "", "translation": ""})

    ########################################################################
    #.............................卡片動畫..................................#
    ########################################################################
    #卡片打出動畫
    def play_card(self, qtype, index):
        if self.IsAnswering and not self.back_to_menu:
            if self.selected_card_index == index:
                # 再次點擊同張卡片 → 還原大小、移除確認按鈕
                self.selected_card_index = None
                self.reposition_cards()
                if self.confirm_button:
                    self.all_sprites.remove(self.confirm_button)
                    self.confirm_button = None
            else:
                # 點擊新卡片 → 全部重排、放大選取卡片、生成確認按鈕
                self.selected_card_index = index
                self.reposition_cards()  # 重繪所有卡片
                self.generate_confirm_button(qtype, index)

    def reposition_cards(self):
        # 移除原有卡片
        for sprite in list(self.all_sprites):
            if isinstance(sprite, Card):
                self.all_sprites.remove(sprite)

        # 重新放置卡片
        for idx, card_data in enumerate(self.choice):
            scale = 2.3 if idx == self.selected_card_index else 2
            y_pos = 950 if idx == self.selected_card_index else 1000
            card = Card(
                pos=(game.CANVAS_WIDTH // 2 - 90 * self.hand_card_num + 250 * idx, y_pos),
                scale=scale,
                id=card_data['Vocabulary'],
                show_eng=(self.question_type != 1),  
                show_chi=(self.question_type != 0)  
            )
            card.setClick(lambda i=idx: self.play_card(self.question_type, i))
            self.all_sprites.add(card)

    def generate_confirm_button(self, qtype, index):
        if self.confirm_button:
            self.all_sprites.remove(self.confirm_button)
        
        def confirm_action():
            self.check_answer(qtype, index)
            # 移除確認按鈕
            if self.confirm_button:
                self.all_sprites.remove(self.confirm_button)
                self.confirm_button = None
            self.selected_card_index = None

        self.confirm_button = Text_Button(
            pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT - 480),
            text='Confirm',
            font_size=70
        )
        self.confirm_button.setClick(confirm_action)
        self.all_sprites.add(self.confirm_button)

    
    ########################################################################
    #.............................答案檢查..................................#
    ########################################################################
    def check_answer(self, qtype, index):
        if not self.result_shown and self.IsAnswering:
            selected = self.choice[index]['Vocabulary']
            self.selected_history.append(selected)
            self.IsAnswering = False
            removed_card = self.choice[index]
            answer_card = self.choice[self.answer_index]
            if selected == self.answer:
                self.choice.remove(removed_card)
                self.voc_list.remove(removed_card)
                self.score += 1
                self.current_result_text = "Correct!"
            else:
                self.current_result_text = f"Wrong! Correct Answer: {self.answer}"
                self.choice.remove(removed_card)
                self.voc_list.remove(removed_card)
                if answer_card in self.choice:
                    self.choice.remove(answer_card)
                if answer_card in self.voc_list:
                    self.voc_list.remove(answer_card)
            self.current_card_num = len(self.choice)
            self.result_shown = True

            if qtype == 2 and self.question:
                self.current_translation_text = f"Translation: {self.question.get('translation', '')}"
            else:
                self.current_translation_text = ""

            next_button = Text_Button(
                pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT - 480),
                text='Next',
            )
            next_button.setClick(lambda: self.load_question(qtype, self.level))
            self.all_sprites.add(next_button)
    
    #顯示結果
    def show_result(self):
        if not self.back_to_menu:
            from ..state import Menu_State
            self.all_sprites.empty()
            self.setMenuButton()
            self.current_title_text = "Result"
            self.current_question_text = ""
            self.current_translation_text = ""
            type_str = ["單字中翻英", "單字英翻中", "例句填空"]
            accuracy = round(self.score / self.question_num * 100, 1)
            lines = [
                f"Your score: {self.score}/{self.question_num}",
                f"Accuracy: {accuracy}%",
                f"Question qtype: {type_str[self.question_type]}",
                ""
            ]

            # 錯題分析
            wrong_list = []
            for i in range(self.question_num):
                correct = self.answer_history[i]
                selected = self.selected_history[i]
                if correct != selected:
                    wrong_list.append(f"Q{i+1}. Correct: {correct} | Your Answer: {selected}")

            if wrong_list:
                lines.append("Wrong Answers:")
                lines.extend(wrong_list)
            else:
                lines.append("Perfect! All correct.")

            # 用 \n 串成 self.current_result_text 供 render 顯示
            self.current_result_text = "\n".join(lines)
            
            review_button = Text_Button(
            pos=(game.CANVAS_WIDTH//2, game.CANVAS_HEIGHT - 100),
            text='Review',
            font_size=70
            )
            review_button.setClick(self.review_answers)
            self.all_sprites.add(review_button)

    ########################################################################
    #...........................回顧答題紀錄................................#
    ########################################################################
    def review_answers(self):
        if not self.back_to_menu:
            self.is_reviewing = True
            self.review_index = 0
            self.show_review_question()
    
    def show_review_question(self):
        if not self.back_to_menu:
            self.all_sprites.empty()
            self.setMenuButton()
            self.result_shown = True  # 啟用翻譯與回饋顯示用
            i = self.review_index
            self.current_title_text = f"Review - Question {i+1}"

            if self.question_type == 0:
                self.current_question_text = next(
                    (c['Translation'] for c in self.choice_history[i] if c['Vocabulary'] == self.answer_history[i]),
                    "[Translation Not Found]"
                )
            elif self.question_type == 1:
                self.current_question_text = self.answer_history[i]
            elif self.question_type == 2:
                question = self.question_history[i]
                if question and 'sentence' in question:
                    self.current_question_text = question['sentence'].replace(self.answer_history[i], '_____')
                else:
                    self.current_question_text = "[No example sentence found]"
                self.current_translation_text = f"Translation: {question.get('translation', '')}" if question else ""
            else:
                self.current_translation_text = ""

            self.current_result_text = (
                f"Correct Answer: {self.answer_history[i]}\n"
                f"Your Answer: {self.selected_history[i]}\n"
                f"{'✓ Correct' if self.selected_history[i] == self.answer_history[i] else '✗ Wrong'}"
            )

            # 上一題按鈕
            if i > 0:
                prev_btn = Text_Button(pos=(100, game.CANVAS_HEIGHT - 100), text="Back", font_size=60)
                prev_btn.setClick(lambda: self.review_nav(-1))
                self.all_sprites.add(prev_btn)

            # 下一題按鈕
            if i < self.question_num - 1:
                next_btn = Text_Button(pos=(game.CANVAS_WIDTH - 100, game.CANVAS_HEIGHT - 100), text="Next", font_size=60)
                next_btn.setClick(lambda: self.review_nav(1))
                self.all_sprites.add(next_btn)

            # 離開回顧
            exit_btn = Text_Button(pos=(game.CANVAS_WIDTH//2, game.CANVAS_HEIGHT - 100), text="Exit Review", font_size=60)
            exit_btn.setClick(self.exit_review)
            self.all_sprites.add(exit_btn)
    
    # 顯示回顧題目
    def review_nav(self, direction: int):
        self.review_index += direction
        self.review_index = max(0, min(self.review_index, self.question_num - 1))
        self.show_review_question()
    
    # 離開回顧
    def exit_review(self):
        self.is_reviewing = False
        self.show_result()

    #遊戲開始
    def start_game(self, qtype, level):
        if not self.back_to_menu:
            self.all_sprites.empty()
            self.setMenuButton()
            self.question_type = qtype
            self.level = level
            self.load_question(qtype, level)

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
    def handle_event(self):
        self.all_sprites.handle_event()

    def update(self):
        self.all_sprites.update()
        if self.is_drawing_cards and self.pending_cards:
            now = pg.time.get_ticks()
            if now - self.card_draw_start_time >= self.card_draw_interval:
                card_data = self.pending_cards.pop(0)
                self.choice.append(card_data)
                self.current_card_num = len(self.choice)
                card = Card(
                    pos=(game.CANVAS_WIDTH // 2 - 90 * self.hand_card_num + 250 * (self.current_card_num - 1), 1000),
                    scale=2,
                    id=card_data['Vocabulary'],
                    show_eng=(self.question_type != 1),  
                    show_chi=(self.question_type != 0)  
                )
                card.setClick(lambda i=self.current_card_num - 1: self.play_card(self.question_type, i))
                self.all_sprites.add(card)
                self.card_draw_start_time = now

            if not self.pending_cards:
                self.is_drawing_cards = False
                self.setup_question_display()

    def render(self):
        Font_Manager.draw_text(game.canvas, self.current_title_text, 70, game.CANVAS_WIDTH/2, 100)
        if self.current_question_text:
            font = pg.font.Font("res\\font\\SWEISANSCJKTC-REGULAR.TTF", 60)
            self.draw_wrapped_text(game.canvas, self.current_question_text, font, (255, 255, 255), 100, 180, game.CANVAS_WIDTH - 200)
       
        if self.result_shown:
            result_lines = self.current_result_text.split('\n')
            for idx, line in enumerate(result_lines):
                Font_Manager.draw_text(game.canvas, line, 50, game.CANVAS_WIDTH//2, 300 + idx * 60)
            if self.current_translation_text:
                Font_Manager.draw_text(game.canvas, self.current_translation_text, 50, game.CANVAS_WIDTH//2, 350 + len(result_lines) * 60)
        self.all_sprites.draw(game.canvas)
        
        if self.back_to_menu:
            dark_overlay = pg.Surface((game.CANVAS_WIDTH, game.CANVAS_HEIGHT), flags=pg.SRCALPHA) #黑幕頁面
            dark_overlay.fill((0, 0, 0, 180))  # RGBA，最後一個值是透明度（0~255）
            game.canvas.blit(dark_overlay, (0, 0))  # 把暗幕畫上去
            Font_Manager.draw_text(game.canvas, self.back_to_menu_text, 50, game.CANVAS_WIDTH//2, 350)
            self.check_group.draw(game.canvas)