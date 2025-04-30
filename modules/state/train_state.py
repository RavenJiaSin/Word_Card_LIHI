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
        self.current_result_text= ""
        #flag設定
        self.back_to_menu = False
        self.result_shown = False
        self.IsAnswering = False
        self.is_drawing_cards = False
        #抽牌設定
        self.card_draw_start_time = 0
        self.card_draw_interval = 150  # 毫秒
        self.pending_cards = []
        #數值設定
        self.score = 0 #分數
        self.question_num = 6 #題數
        self.question_count = 0 #目前題數
        self.hand_card_num = 6 #手牌數量
        self.current_card_num = 0 #目前手牌數量
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
            btn = Text_Button(pos=(game.CANVAS_WIDTH/2, 400 + i*200), scale=1, text="LEVEL"+str(i+1), font_size=70)
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
        btn1 = Text_Button(pos=(game.CANVAS_WIDTH/2, 400), scale=1, text="單字中翻英", font_size=70)
        btn1.setClick(lambda type=0: self.start_game(type, level))
        self.difficulty_buttons.append(btn1)
        self.all_sprites.add(btn1)

        btn2 = Text_Button(pos=(game.CANVAS_WIDTH/2, 600), scale=1, text="單字英翻中", font_size=70)
        btn2.setClick(lambda type=1: self.start_game(type, level))
        self.difficulty_buttons.append(btn2)
        self.all_sprites.add(btn2)

        btn3 = Text_Button(pos=(game.CANVAS_WIDTH/2, 800), scale=1, text="例句填空", font_size=70)
        btn3.setClick(lambda type=2: self.start_game(type, level))
        self.difficulty_buttons.append(btn3)
        self.all_sprites.add(btn3)

    ########################################################################
    #.............................載入題目..................................#
    ########################################################################
    
    def load_question(self, type, level):
        if self.question_count < self.question_num:
            if self.current_card_num == 0:
                from modules.database import VocabularyDB
                self.question_history = []
                self.card_history = []
                self.answer_history = []
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
                    pos=(game.CANVAS_WIDTH // 2 - 80 * self.hand_card_num + 190 * idx, 850),
                    scale=1.5,
                    id=card_data['Vocabulary']
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

        if self.question_type == 0:
            self.current_question_text = self.choice[self.answer_index]['Translation']
        elif self.question_type == 1:
            self.current_question_text = self.choice[self.answer_index]['Vocabulary']
        elif self.question_type == 2:
            self.question = self.db.get_example_sentences(voc_id=self.choice[self.answer_index]['ID'])[0]
            sentence = self.question['sentence']
            self.current_question_text = sentence.replace(self.answer, "_____")
            self.question_history.append(self.question)
            
    #卡片打出動畫
    def play_card(self, type, index):
        self.check_answer(type, index)#下面完成後刪除這行
        #移動卡片位置
        #卡片打出後新增按鈕進行確認=>self.check_answer(type, index)
        #取消卡片打出事件，將卡片復原
        
    ########################################################################
    #.............................答案檢查..................................#
    ########################################################################
    def check_answer(self, type, index):
        if not self.result_shown and self.IsAnswering:
            selected = self.choice[index]['Vocabulary']
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

    #遊戲開始
    def start_game(self, type, level):
        self.all_sprites.empty()
        self.setMenuButton()
        self.question_type = type
        self.level = level
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
    def handle_event(self):
        self.all_sprites.handle_event()

    def update(self):
        self.all_sprites.update()
        if self.is_drawing_cards and self.pending_cards:
            now = pg.time.get_ticks()
            if now - self.card_draw_start_time >= self.card_draw_interval:
                card_data = self.pending_cards.pop(0)
                self.choice.append(card_data)
                self.choice_history.append(self.choice[:])
                self.current_card_num = len(self.choice)
                card = Card(
                    pos=(game.CANVAS_WIDTH // 2 - 80 * self.hand_card_num + 190 * (self.current_card_num - 1), 850),
                    scale=1.5,
                    id=card_data['Vocabulary']
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
            Font_Manager.draw_text(game.canvas, self.current_result_text, 50, game.CANVAS_WIDTH//2, 350)
            Font_Manager.draw_text(game.canvas, self.current_translation_text, 50, game.CANVAS_WIDTH//2, 450)
        self.all_sprites.draw(game.canvas)
        
        if self.back_to_menu:
            dark_overlay = pg.Surface((game.CANVAS_WIDTH, game.CANVAS_HEIGHT), flags=pg.SRCALPHA) #黑幕頁面
            dark_overlay.fill((0, 0, 0, 180))  # RGBA，最後一個值是透明度（0~255）
            game.canvas.blit(dark_overlay, (0, 0))  # 把暗幕畫上去
            Font_Manager.draw_text(game.canvas, self.current_result_text, 50, game.CANVAS_WIDTH//2, 350)
            self.check_group.draw(game.canvas)
            
