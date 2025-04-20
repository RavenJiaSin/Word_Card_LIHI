import pygame as pg
import random
import game
from modules.database import VocabularyDB
from .state import State
from ..object import Text_Button
from ..object import Card
from ..manager import img_map

class Train_State(State):

    def __init__(self):
        from ..state import Menu_State  # 在這邊import是為了避免circular import
        self.all_sprites = pg.sprite.Group()
        #更改按鈕位置大小
        button_x = 150
        button_wh = (60, 45)
        
        menu_button = Text_Button(pos=(game.WINDOW_WIDTH-60,game.WINDOW_HEIGHT-60), size=button_wh, text='BACK')
        menu_button.setClick(lambda:game.chage_state(Menu_State()))
        self.all_sprites.add(menu_button)
        self.difficulty_select()


    # 難度選擇
    def difficulty_select(self):
        self.all_sprites.empty()
        self.difficulty_buttons = []
        self.level = 0
        print("Difficulty Select")
        for i in range(3):
            btn = Text_Button(pos=(game.WINDOW_WIDTH/2, 250 + i*70), size=(400, 50), text="LEVEL"+str(i+1))
            btn.setClick(lambda level=i+1: self.start_game(level))
            self.difficulty_buttons.append(btn)
            self.all_sprites.add(btn)
    
    # 題目建構
        #1.根據難度選擇隨機抓取4個資料庫中的單字 
        #2.隨機選擇一個單字作為答案
        #3.將答案所對應的例句挖空作為題目
        #4.將剩餘的3個單字作為選項
    def load_question(self,level):
        if self.question_count < self.question_num:
            if self.question_count == 0:
                from modules.database import VocabularyDB
                self.question_history = []
                self.answer_history = []
                self.level = level
                # 載入資料庫中的單字
                self.db = VocabularyDB()
                self.voc_list=[ ('4401_sack', 'sack', 'n.', '袋;粗布袋', 3), ('4402_sake', 'sake', 'n.', '理由;緣故;利益', 3), 
                                ('4403_saucer', 'saucer', 'n.', '淺碟', 3), ('4404_sausage', 'sausage', 'n.', '香腸,臘腸', 3), 
                                ('4405_saving', 'saving', 'n.', '挽救;節儉,節約;儲金', 3), ('4406_scale', 'scale', 'n.', '尺度;等級;級別', 3), 
                                ('4407_scarecrow', 'scarecrow', 'n.', '稻草人;威嚇物', 3), ('4408_scarf', 'scarf', 'n.', '圍巾', 3)]
            print("Question Count: ", self.question_count)
            print("Question Num: ", self.question_num)
            self.question_count += 1
            self.all_sprites.empty()
            self.question = []
            self.result_shown = False
            '''
            voc_list = db.find_vocabulary(level)
            print(f"Vocabulary List: {voc_list}")
            '''
            print("Question",self.question_count)
            game.draw_text(game.window, str(self.question_count), 30, game.WINDOW_WIDTH/2, 100)
            self.all_sprites.draw(game.window)
            # 隨機選擇4個單字
            self.choice = random.sample(self.voc_list, 4)
            # 隨機選擇一個單字作為答案
            self.answer_index = random.randint(0, 3)
            self.answer = self.choice[self.answer_index][1]    
            # 將答案所對應的例句挖空作為題目
            self.question = self.db.get_example_sentences(voc_id=self.choice[self.answer_index][0]) 
            #尚未完成挖空
            
            #print("Vocabulary List: ", self.choice) 
            print("Answer: ", self.answer)   
            print("Question: ", self.question[0][2])
            # 顯示題目
            game.draw_text(game.window, str(self.question[0][2]), 30, game.WINDOW_WIDTH/2, 100)
            self.all_sprites.draw(game.window)
            # 顯示選項                
            for i in range(4):
                btn = Text_Button(pos=(game.WINDOW_WIDTH/2, 250 + i*70), size=(400, 50), text=self.choice[i][1])
                print("Choice",i+1, self.choice[i][1])
                btn.setClick(lambda i=i:self.check_answer(self.choice[i][1]))
                self.all_sprites.add(btn)
        else:
            self.show_result()
        
    def check_answer(self, selected):
        print("Selected: ", selected)
        if not self.result_shown:
            if selected == self.answer:
                self.score += 1
                self.result_shown = True
                print("Correct! Score: ", self.score)
            else:
                print("Wrong! Correct answer is: ", self.answer)
                self.result_shown = True
            
            # 顯示正確答案和翻譯
            correct_answer_text = f"Correct Answer: {self.answer}"
            translation_text = f"Translation: {self.question[0][3]}"
            print(correct_answer_text)
            print(translation_text)
            
        next_button = Text_Button(pos=(game.WINDOW_WIDTH-60,game.WINDOW_HEIGHT-60), size=(60, 50), text='Next')
        next_button.setClick(lambda: self.load_question(self.level))
        self.all_sprites.add(next_button)
    
    # 開始遊戲
    def start_game(self, level):
        self.all_sprites.empty()
        self.level = level
        self.score = 0
        self.question_num = 3
        self.question_count = 0
        self.result_shown = False
        self.load_question(level)
        
    # 檢查答案
        #1.如果選擇的答案正確，顯示正確，並且加1分(可同時記錄其他資訊)
        #2.如果選擇的答案錯誤，顯示錯誤，並且不加分(可同時記錄其他資訊)
        #3.顯示正確答案
        #4.顯示例句的翻譯
        #5.顯示下一題按鈕
        
    # 顯示結果
    def show_result(self):
        from ..state import Menu_State 
        self.all_sprites.empty()
        result_text = f"Your score: {self.score}/{self.question_num}"
        game.draw_text(game.window, result_text, 50, game.WINDOW_WIDTH/2, game.WINDOW_HEIGHT/2)
        self.result_shown = True
        back_btn = Text_Button(pos=(game.WINDOW_WIDTH/2, game.WINDOW_HEIGHT/2 + 80), size=(120, 60), text="Back to Menu")
        back_btn.setClick(lambda: game.chage_state(Menu_State()))
        self.all_sprites.add(back_btn)
    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        game.draw_text(game.window, "Test", 50, game.WINDOW_WIDTH/2, 50)
        self.all_sprites.draw(game.window)