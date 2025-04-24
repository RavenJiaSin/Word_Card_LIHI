import pygame as pg
import random
import game
from modules.database import VocabularyDB
from .state import State
from ..object import Text_Button
#from ..object import Card
#from ..manager import Image_Manager

class Train_State(State):

    def __init__(self):
        from ..state import Menu_State  # 在這邊import是為了避免circular import
        self.all_sprites = pg.sprite.Group()
        #文字初始化
        self.current_title_text = "Train Room!"
        self.current_question_text = ""
        self.current_result_text = ""
        self.current_translation_text = ""
        #參數初始化
        self.score = 0
        self.result_shown = False
        self.question_num = 4
        self.question_count = 0
        self.IsAnswering= False

        menu_button = Text_Button(
            pos=(game.CANVAS_WIDTH - 120, game.CANVAS_HEIGHT - 80), 
            size=(200, 80), 
            text='MENU', 
            font_size=70, 
            font='SWEISANSCJKTC-REGULAR'
        )
        menu_button.setClick(lambda:game.change_state(Menu_State()))
        self.all_sprites.add(menu_button)
        self.difficulty_select()


    # 難度選擇
    def difficulty_select(self):
        from ..state import Menu_State
        self.all_sprites.empty()
        self.difficulty_buttons = []
        self.level = 0
        for i in range(3):
            btn = Text_Button(
                pos=(game.CANVAS_WIDTH/2, 400 + i*200), 
                size=(400, 150), 
                text="LEVEL"+str(i+1), 
                font_size=70, 
                font='SWEISANSCJKTC-REGULAR'
                )
            btn.setClick(lambda level=i+1: self.question_type_select(level))
            self.difficulty_buttons.append(btn)
            self.all_sprites.add(btn)
        back_btn = Text_Button(
            pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT-80), 
            size=(200, 80), 
            text="Menu", 
            font_size=70, 
            font='SWEISANSCJKTC-REGULAR'
        )
        back_btn.setClick(lambda: game.change_state(Menu_State()))
        self.all_sprites.add(back_btn)
    
    
    # 題型選擇(例句填空or單字翻譯)
    def question_type_select(self,level):
        from ..state import Menu_State
        self.all_sprites.empty()
        self.difficulty_buttons = []
        self.question_type = 0
        #單字翻譯
        btn1 = Text_Button(
            pos=(game.CANVAS_WIDTH/2, 400), 
            size=(400, 150), 
            text="單字中翻英", 
            font_size=70, 
            font='SWEISANSCJKTC-REGULAR'
            )
        btn1.setClick(lambda type=0: self.start_game(type,level))
        self.difficulty_buttons.append(btn1)
        self.all_sprites.add(btn1)
        
        btn2 = Text_Button(
            pos=(game.CANVAS_WIDTH/2, 600), 
            size=(400, 150), 
            text="單字英翻中", 
            font_size=70, 
            font='SWEISANSCJKTC-REGULAR'
            )
        btn2.setClick(lambda type=1: self.start_game(type,level))
        self.difficulty_buttons.append(btn2)
        self.all_sprites.add(btn2)
        
        #例句填空
        btn3 = Text_Button(
            pos=(game.CANVAS_WIDTH/2, 800), 
            size=(400, 150), 
            text="例句填空", 
            font_size=70, 
            font='SWEISANSCJKTC-REGULAR'
            )
        btn3.setClick(lambda type=2: self.start_game(type,level))
        self.difficulty_buttons.append(btn3)
        self.all_sprites.add(btn3)
        
        back_btn = Text_Button(
            pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT-80), 
            size=(200, 80), 
            text="Menu", 
            font_size=70, 
            font='SWEISANSCJKTC-REGULAR'
        )
        back_btn.setClick(lambda: game.change_state(Menu_State()))
        self.all_sprites.add(back_btn)
    
    # 題目建構
        #1.根據難度選擇隨機抓取4個資料庫中的單字 
        #2.隨機選擇一個單字作為答案
        #3.將答案所對應的例句挖空作為題目
        #4.將剩餘的3個單字作為選項
    def load_question(self,type,level):
        if self.question_count < self.question_num:
            if self.question_count == 0:
                from modules.database import VocabularyDB
                self.question_history = []
                self.answer_history = []
                self.level = level
                # 載入資料庫中的單字
                self.db = VocabularyDB()
                '''
                self.voc_list = self.db.find_vocabulary(level)
                '''
                self.voc_list=[ ('4401_sack', 'sack', 'n.', '袋;粗布袋', 3), ('4402_sake', 'sake', 'n.', '理由;緣故;利益', 3), 
                                ('4403_saucer', 'saucer', 'n.', '淺碟', 3), ('4404_sausage', 'sausage', 'n.', '香腸,臘腸', 3), 
                                ('4405_saving', 'saving', 'n.', '挽救;節儉,節約;儲金', 3), ('4406_scale', 'scale', 'n.', '尺度;等級;級別', 3), 
                                ('4407_scarecrow', 'scarecrow', 'n.', '稻草人;威嚇物', 3), ('4408_scarf', 'scarf', 'n.', '圍巾', 3)]
            self.IsAnswering = True
            self.question_count += 1
            self.all_sprites.empty()
            self.question = []
            self.result_shown = False
            self.current_title_text="Question "+str(self.question_count)+"/"+str(self.question_num)
            # 隨機選擇4個單字
            self.choice = random.sample(self.voc_list, 4)
            # 隨機選擇一個單字作為答案
            self.answer_index = random.randint(0, 3)
            self.answer = self.choice[self.answer_index][1]    
            # 將答案所對應的例句挖空/單字對應翻譯作為題目
            if type==0:#0:單字中翻英 1:單字英翻中 2:例句填空
                self.answer = self.choice[self.answer_index][1]     
                self.question = self.choice[self.answer_index]
                self.current_question_text = self.question[3]
            elif type==1:
                self.answer = self.choice[self.answer_index][3]
                self.question = self.choice[self.answer_index]
                self.current_question_text = self.question[1]
            elif type==2:
                self.answer = self.choice[self.answer_index][1]
                self.question = self.db.get_example_sentences(voc_id=self.choice[self.answer_index][0]) 
                sentence = self.question[0][2]
                self.current_question_text = sentence.replace(self.answer, "_____")
            print(self.question)
            # 顯示選項                
            for i in range(4):
                if type==1:
                    btn = Text_Button(
                    pos=(game.CANVAS_WIDTH // 2, 400 + i * 150), 
                    size=(600, 100), 
                    text=self.choice[i][3], 
                    font_size=70, 
                    font='SWEISANSCJKTC-REGULAR'
                    )
                    btn.setClick(lambda i=i:self.check_answer(type, self.choice[i][3]))
                else:
                    btn = Text_Button(
                    pos=(game.CANVAS_WIDTH // 2, 400 + i * 150), 
                    size=(600, 100), 
                    text=self.choice[i][1], 
                    font_size=70, 
                    font='SWEISANSCJKTC-REGULAR'
                    )
                    btn.setClick(lambda i=i:self.check_answer(type, self.choice[i][1]))
                self.all_sprites.add(btn)
        else:
            self.show_result()
        
    # 檢查答案
        #1.如果選擇的答案正確，顯示正確，並且加1分(可同時記錄其他資訊)
        #2.如果選擇的答案錯誤，顯示錯誤，並且不加分(可同時記錄其他資訊)
        #3.顯示正確答案
        #4.顯示例句的翻譯
        #5.顯示下一題按鈕
    def check_answer(self, type, selected):
        print("Selected: ", selected)
        if self.IsAnswering:
            self.IsAnswering = False
            if not self.result_shown:
                if selected == self.answer:
                    self.score += 1
                    self.current_result_text = "Correct!"
                    self.result_shown = True
                else:
                    self.current_result_text = f"Wrong! Correct Answer: {self.answer}"
                    self.result_shown = True
                
                # 顯示正確答案和翻譯
                if type==0:#0:單字中翻英 1:單字英翻中 2:例句填空
                    self.current_translation_text = f"Translation: {self.question[0][3]}"
                elif type==1:
                    self.current_translation_text = f"Translation: {self.question[0][1]}"
                elif type==2:
                    self.current_translation_text = f"Translation: {self.question[0][3]}"
                
            next_button = Text_Button(
            pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT-80), 
                size=(200, 80), 
                text='Next', 
                font_size=70, 
                font='SWEISANSCJKTC-REGULAR'
            )
            next_button.setClick(lambda: self.load_question(type, self.level))
            self.all_sprites.add(next_button)
    
    # 顯示結果
    def show_result(self):
        from ..state import Menu_State 
        self.all_sprites.empty()
        self.current_title_text = "Result"
        self.current_question_text = ""
        self.current_translation_text = ""
        self.current_result_text = f"Your score: {self.score}/{self.question_num}"
        self.result_shown = True
        back_btn = Text_Button(
            pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT-80), 
            size=(200, 80), 
            text="Menu", 
            font_size=70, 
            font='SWEISANSCJKTC-REGULAR'
        )
        back_btn.setClick(lambda: game.change_state(Menu_State()))
        self.all_sprites.add(back_btn)
        
    # 開始遊戲
    def start_game(self,type,level):
        self.all_sprites.empty()
        self.question_type = type
        self.level = level
        self.load_question(type,level)
    
    # 顯示文字
    def draw_wrapped_text(surface, text, font, color, x, y, max_width, line_spacing=10):
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
        lines.append(line)  # append last line

        for i, line in enumerate(lines):
            rendered_line = font.render(line.strip(), True, color)
            surface.blit(rendered_line, (x, y + i * (font.get_linesize() + line_spacing)))
        
    # override
    def handle_event(self):
        ...
        
    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        game.draw_text(game.canvas, self.current_title_text, 70, game.CANVAS_WIDTH/2, 100)
        # 顯示題目
        if self.current_question_text:
            game.draw_text(game.canvas, self.current_question_text, 60, game.CANVAS_WIDTH//2, 180)
        # 顯示正解與翻譯（若有）
        if self.result_shown:
            game.draw_text(game.canvas, self.current_result_text, 40, game.CANVAS_WIDTH//2, 250)
            game.draw_text(game.canvas, self.current_translation_text, 40, game.CANVAS_WIDTH//2, 300)
        self.all_sprites.draw(game.canvas)