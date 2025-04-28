import pygame as pg
import random
import game
from modules.database import VocabularyDB
from .state import State
from ..object import Text_Button
from ..manager import Font_Manager
from ..object import Card
from ..manager import Image_Manager

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
        self.end_card_num = 2         # 剩下幾張卡片時結束
        self.max_card_num = 8          # 最大手牌數量        
        menu_button = Text_Button(
            pos=(game.CANVAS_WIDTH - 120, game.CANVAS_HEIGHT - 80), 
            scale=1,
            #size=(200, 80), 
            text='MENU', 
            font_size=70, 
            
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
                scale=1,
                #size=(400, 150), 
                text="LEVEL"+str(i+1), 
                font_size=70, 
                
                )
            btn.setClick(lambda level=i+1: self.question_type_select(level))
            self.difficulty_buttons.append(btn)
            self.all_sprites.add(btn)
        back_btn = Text_Button(
            pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT-80), 
            scale=1,
            #size=(200, 80), 
            text="Menu", 
            font_size=70, 
            
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
            scale=1,
            #size=(400, 150), 
            text="單字中翻英", 
            font_size=70, 
            
            )
        btn1.setClick(lambda type=0: self.start_game(type,level))
        self.difficulty_buttons.append(btn1)
        self.all_sprites.add(btn1)
        
        btn2 = Text_Button(
            pos=(game.CANVAS_WIDTH/2, 600), 
            scale=1,
            #size=(400, 150), 
            text="單字英翻中", 
            font_size=70, 
            
            )
        btn2.setClick(lambda type=1: self.start_game(type,level))
        self.difficulty_buttons.append(btn2)
        self.all_sprites.add(btn2)
        
        #例句填空
        btn3 = Text_Button(
            pos=(game.CANVAS_WIDTH/2, 800), 
            scale=1,
            #size=(400, 150), 
            text="例句填空", 
            font_size=70, 
            
            )
        btn3.setClick(lambda type=2: self.start_game(type,level))
        self.difficulty_buttons.append(btn3)
        self.all_sprites.add(btn3)
        
        back_btn = Text_Button(
            pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT-80), 
            scale=1,
            #size=(200, 80), 
            text="Menu", 
            font_size=70, 
            
        )
        back_btn.setClick(lambda: game.change_state(Menu_State()))
        self.all_sprites.add(back_btn)
            
    def load_question(self,type,level):
        if self.current_card_num > self.end_card_num:
            if self.current_card_num == self.max_card_num:
                from modules.database import VocabularyDB
                self.question_history = []
                self.card_history = []
                self.answer_history = []
                self.level = level
                self.db = VocabularyDB()
                '''
                # 載入擁有牌庫中的資料
                self.voc_list = self.db.find_vocabulary(level)
                '''
                #建立牌庫
                self.voc_list=[ ('4401_sack', 'sack', 'n.', '袋;粗布袋', 3), ('4402_sake', 'sake', 'n.', '理由;緣故;利益', 3), 
                                ('4403_saucer', 'saucer', 'n.', '淺碟', 3), ('4404_sausage', 'sausage', 'n.', '香腸,臘腸', 3), 
                                ('4405_saving', 'saving', 'n.', '挽救;節儉,節約;儲金', 3), ('4406_scale', 'scale', 'n.', '尺度;等級;級別', 3), 
                                ('4407_scarecrow', 'scarecrow', 'n.', '稻草人;威嚇物', 3), ('4408_scarf', 'scarf', 'n.', '圍巾', 3)]
                
                # 隨機選擇手牌上限數量個單字
                self.choice = random.sample(self.voc_list, self.max_card_num)
                self.choice_history=self.choice
                self.current_card_num = len(self.choice)
            self.IsAnswering = True
            self.question_count += 1
            self.all_sprites.empty()
            self.question = []
            self.result_shown = False
            self.current_title_text="Question "+str(self.question_count)
            # 隨機選擇一個單字作為答案
            self.answer_index = random.randint(0, self.current_card_num-1)
            self.answer = self.choice[self.answer_index][1]
            self.answer_history.append(self.answer)
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
                self.question = self.db.get_example_sentences(voc_id=self.choice[self.answer_index][0])[0]
                sentence = self.question['sentence']
                self.current_question_text = sentence.replace(self.answer, "_____")
            self.question_history.append(self.question)
            print(self.question)
            print(self.answer)
            # 顯示卡片                
            for i in range(self.current_card_num):
                card = Card(
                    pos=(game.CANVAS_WIDTH // 2-720+250*i, 600), 
                    scale=2,
                    id=self.choice[i][1], 
                )
                card.setClick(lambda i=i:self.check_answer(type, i))
                self.all_sprites.add(card)
            
        else:
            self.show_result()
            print("Question History",self.question_history)
            print("Choice History",self.choice_history)
            print("Answer History",self.answer_history)
    
    
    
    # 檢查答案
        #1.如果選擇的答案正確，顯示正確，並且加1分(可同時記錄其他資訊)
        #2.如果選擇的答案錯誤，顯示錯誤，並且不加分(可同時記錄其他資訊)
        #3.顯示正確答案
        #4.顯示例句的翻譯
        #5.顯示下一題按鈕
    def check_answer(self, type, index):
        selected=self.choice[index][1]
        self.choice.remove(self.choice[index])
        self.current_card_num = len(self.choice)
        print(self.choice)
        print("Selected: ", selected)
        if self.IsAnswering:
            print("Is Answering")
            self.IsAnswering = False
            if not self.result_shown:
                print("Not Shown")
                if selected == self.answer:
                    self.score += 1
                    self.current_result_text = "Correct!"
                    self.result_shown = True
                else:
                    self.current_result_text = f"Wrong! Correct Answer: {self.answer}"
                    self.result_shown = True
                
                # 顯示正確答案和翻譯
                if type==2:#0:單字中翻英 1:單字英翻中 2:例句填空
                    self.current_translation_text = f"Translation: {self.question['translation']}"
                
            next_button = Text_Button(
            pos=(game.CANVAS_WIDTH // 2, game.CANVAS_HEIGHT-80), 
                scale=1,
                #size=(200, 80), 
                text='Next', 
                font_size=70, 
                
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
            scale=1,
            #size=(200, 80), 
            text="Menu", 
            font_size=70, 
            
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
    def draw_wrapped_text(self, surface: pg.Surface, text: str, font: pg.font.Font, color: tuple, x: int, y: int, max_width: int, line_spacing: int = 10) -> None:
        """自動換行繪製文字"""
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
        
    # override
    def handle_event(self):
        ...
        
    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, self.current_title_text, 70, game.CANVAS_WIDTH/2, 100)
        # 顯示題目
        if self.current_question_text:
            font = pg.font.Font("res\\font\SWEISANSCJKTC-REGULAR.TTF", 60)
            self.draw_wrapped_text(game.canvas, self.current_question_text, font, (255, 255, 255), 100, 180, game.CANVAS_WIDTH - 200)
        # 顯示正解與翻譯（若有）
        if self.result_shown:
            Font_Manager.draw_text(game.canvas, self.current_result_text, 50, game.CANVAS_WIDTH//2, 350)
            Font_Manager.draw_text(game.canvas, self.current_translation_text, 50, game.CANVAS_WIDTH//2, 450)
        self.all_sprites.draw(game.canvas)