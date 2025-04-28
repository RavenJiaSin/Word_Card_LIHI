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
        from ..state import Menu_State
        self.all_sprites = pg.sprite.Group()
        self.current_title_text = "Train Room!"
        self.current_question_text = ""
        self.current_result_text = ""
        self.current_translation_text = ""
        self.current_result_text= ""
        self.back_to_menu = False
        self.score = 0
        self.result_shown = False
        self.question_num = 6
        self.question_count = 0
        self.IsAnswering = False
        self.end_card_num = 2
        self.max_card_num = 8
        self.current_card_num = self.max_card_num
        menu_button = Text_Button(pos=(game.CANVAS_WIDTH - 120, game.CANVAS_HEIGHT - 80), scale=1, text='MENU', font_size=70)
        menu_button.setClick(lambda: game.change_state(Menu_State()))
        self.all_sprites.add(menu_button)
        self.difficulty_select()
        
    def setMenuButton(self):
        menu_button = Text_Button(pos=(100,100), scale=1, text='Menu', font_size=40)
        menu_button.setClick(lambda:Train_State.check_go_to_menu(self))
        self.all_sprites.add(menu_button)
        
    def check_go_to_menu(self):
        self.current_result_text= "Are you sure to go back to menu?"
        self.IsAnswering = False
        self.back_to_menu = True
        self.checkbtnY = Text_Button(pos=(game.CANVAS_WIDTH/2-200, game.CANVAS_HEIGHT/2), scale=1, text="Yes", font_size=70)
        self.checkbtnY.setClick(lambda: self.go_to_menu())
        self.checkbtnN = Text_Button(pos=(game.CANVAS_WIDTH/2+200, game.CANVAS_HEIGHT/2), scale=1, text="No", font_size=70)
        self.checkbtnN.setClick(lambda : self.cancel_go_to_menu())
        self.all_sprites.add(self.checkbtnY, self.checkbtnN)
        
    def cancel_go_to_menu(self):
        self.back_to_menu = False
        self.IsAnswering = True
        self.current_result_text= ""
        self.all_sprites.remove(self.checkbtnY)
        self.all_sprites.remove(self.checkbtnN)
        
    def go_to_menu(self):
        game.background_color = (30,30,30)
        from .menu_state import Menu_State
        game.change_state(Menu_State())
        
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


    def load_question(self, type, level):
        if self.current_card_num > self.end_card_num:
            if self.current_card_num == self.max_card_num:
                from modules.database import VocabularyDB
                self.question_history = []
                self.card_history = []
                self.answer_history = []
                self.level = level
                self.db = VocabularyDB()
                self.voc_list = [
                    {'ID': '4522_ton', 'Vocabulary': 'ton', 'Part_of_speech': 'n.', 'Translation': '噸', 'Level': 3},
                    {'ID': '4523_tortoise', 'Vocabulary': 'tortoise', 'Part_of_speech': 'n.', 'Translation': '陸龜;龜,烏龜', 'Level': 3},
                    {'ID': '4524_toss', 'Vocabulary': 'toss', 'Part_of_speech': 'n.', 'Translation': '擲幣賭勝負', 'Level': 3},
                    {'ID': '4525_tourism', 'Vocabulary': 'tourism', 'Part_of_speech': 'n.', 'Translation': '旅遊,觀光', 'Level': 3},
                    {'ID': '4526_tourist', 'Vocabulary': 'tourist', 'Part_of_speech': 'n.', 'Translation': '旅遊者,觀光者', 'Level': 3},
                    {'ID': '4527_tow', 'Vocabulary': 'tow', 'Part_of_speech': 'n.', 'Translation': '拖,拉;牽引;拖輪;拖曳車', 'Level': 3},
                    {'ID': '4528_trace', 'Vocabulary': 'trace', 'Part_of_speech': 'n.', 'Translation': '蹤跡', 'Level': 3},
                    {'ID': '4529_trader', 'Vocabulary': 'trader', 'Part_of_speech': 'n.', 'Translation': '商人;交易人', 'Level': 3},
                    {'ID': '4530_trail', 'Vocabulary': 'trail', 'Part_of_speech': 'n.', 'Translation': '拖曳物,尾部', 'Level': 3},
                    {'ID': '4531_transport', 'Vocabulary': 'transport', 'Part_of_speech': 'n.', 'Translation': '交通工具', 'Level': 3},
                    {'ID': '4532_trash', 'Vocabulary': 'trash', 'Part_of_speech': 'n.', 'Translation': '垃圾', 'Level': 3},
                    {'ID': '4533_traveler', 'Vocabulary': 'traveler', 'Part_of_speech': 'n.', 'Translation': '旅客;遊客', 'Level': 3},
                    {'ID': '4534_tray', 'Vocabulary': 'tray', 'Part_of_speech': 'n.', 'Translation': '盤子,托盤', 'Level': 3},
                    {'ID': '4535_tremble', 'Vocabulary': 'tremble', 'Part_of_speech': 'n.', 'Translation': '震顫,發抖', 'Level': 3},
                    {'ID': '4536_trend', 'Vocabulary': 'trend', 'Part_of_speech': 'n.', 'Translation': '趨勢,傾向;時尚', 'Level': 3},
                    {'ID': '4537_tribe', 'Vocabulary': 'tribe', 'Part_of_speech': 'n.', 'Translation': '部落;種族', 'Level': 3},
                    {'ID': '4538_troop', 'Vocabulary': 'troop', 'Part_of_speech': 'n.', 'Translation': '軍隊,部隊', 'Level': 3},
                    {'ID': '4539_trunk', 'Vocabulary': 'trunk', 'Part_of_speech': 'n.', 'Translation': '樹幹;大血管', 'Level': 3},
                    {'ID': '4540_tub', 'Vocabulary': 'tub', 'Part_of_speech': 'n.', 'Translation': '浴缸', 'Level': 3},
                    {'ID': '4541_tug', 'Vocabulary': 'tug', 'Part_of_speech': 'n.', 'Translation': '牽引,拖曳', 'Level': 3}
                ]
                self.choice = random.sample(self.voc_list, self.max_card_num)
                self.choice_history = self.choice
                self.current_card_num = len(self.choice)
            self.IsAnswering = True
            self.question_count += 1
            self.all_sprites.empty()
            self.setMenuButton()
            self.question = []
            self.result_shown = False
            self.current_title_text = "Question " + str(self.question_count)
            self.answer_index = random.randint(0, self.current_card_num-1)
            self.answer = self.choice[self.answer_index]['Vocabulary']
            self.answer_history.append(self.answer)
            if type == 0:
                self.answer = self.choice[self.answer_index]['Vocabulary']
                self.question = self.choice[self.answer_index]
                self.current_question_text = self.question['Translation']
            elif type == 1:
                self.answer = self.choice[self.answer_index]['Translation']
                self.question = self.choice[self.answer_index]
                self.current_question_text = self.question['Vocabulary']
            elif type == 2:
                self.answer = self.choice[self.answer_index]['Vocabulary']
                self.question = self.db.get_example_sentences(voc_id=self.choice[self.answer_index]['ID'])[0]
                sentence = self.question['sentence']
                self.current_question_text = sentence.replace(self.answer, "_____")
            self.question_history.append(self.question)
            for i in range(self.current_card_num):
                card = Card(
                    pos=(game.CANVAS_WIDTH // 2-80*self.current_card_num+190*i, 850),
                    scale=1.5,
                    id=self.choice[i]['Vocabulary']
                )
                card.setClick(lambda i=i: self.play_card(type, i))
                self.all_sprites.add(card)
        else:
            self.show_result()
    
    #卡片打出動畫
    def play_card(self, type, index):
        self.check_answer(type, index)

    def check_answer(self, type, index):
        selected = self.choice[index]['Vocabulary']
        if not self.result_shown and self.IsAnswering:
            self.IsAnswering = False
            self.choice.remove(self.choice[index])
            self.current_card_num = len(self.choice)
            if selected == self.answer:
                self.score += 1
                self.current_result_text = "Correct!"
            else:
                self.current_result_text = f"Wrong! Correct Answer: {self.answer}"
                self.choice.remove(self.choice[index])
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

    def show_result(self):
        from ..state import Menu_State
        self.all_sprites.empty()
        self.setMenuButton()
        self.current_title_text = "Result"
        self.current_question_text = ""
        self.current_translation_text = ""
        self.current_result_text = f"Your score: {self.score}/{self.question_num}"
        self.result_shown = True

    def start_game(self, type, level):
        self.all_sprites.empty()
        self.setMenuButton()
        self.question_type = type
        self.level = level
        self.load_question(type, level)

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

    def handle_event(self):
        ...

    def update(self):
        self.all_sprites.update()

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
            Font_Manager.draw_text(game.canvas, self.current_result_text, 50, game.CANVAS_WIDTH//2, 350)
            dark_overlay = pg.Surface((game.CANVAS_WIDTH, game.CANVAS_HEIGHT), flags=pg.SRCALPHA) #黑幕頁面
            dark_overlay.fill((0, 0, 0, 180))  # RGBA，最後一個值是透明度（0~255）
            game.canvas.blit(dark_overlay, (0, 0))  # 把暗幕畫上去
