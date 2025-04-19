import pygame as pg
import random
import game
from .state import State
from ..object import Button
from ..object import Card
from ..manager import img_map

class Practice_State(State):

    def __init__(self):
        from ..state import Menu_State  # 避免 circular import
        self.all_sprites = pg.sprite.Group()
        self.font_path = "C:/Windows/Fonts/msjh.ttc"
        self.font_size = 36

        # 假資料題庫
        self.questions = [
            {
                "sentence": "She is very _____ to help others.",
                "answer": "willing",
                "choices": ["strong", "willing", "lazy", "funny"],
                "translation": "她非常樂意幫助別人。"
            },
            {
                "sentence": "The sun _____ in the east.",
                "answer": "rises",
                "choices": ["shines", "rises", "falls", "moves"],
                "translation": "太陽從東邊升起。"
            },
            {
                "sentence": "He bought a _____ car last week.",
                "answer": "new",
                "choices": ["red", "new", "fast", "old"],
                "translation": "他上週買了一台新車。"
            },
            {
                "sentence": "I usually go to school by _____.",
                "answer": "bus",
                "choices": ["bike", "train", "bus", "car"],
                "translation": "我通常搭公車上學。"
            },
            {
                "sentence": "They _____ their homework before dinner.",
                "answer": "finished",
                "choices": ["finished", "watched", "played", "cleaned"],
                "translation": "他們在晚餐前完成了作業。"
            },
            {
                "sentence": "We had a great time at the _____.",
                "answer": "party",
                "choices": ["school", "party", "zoo", "beach"],
                "translation": "我們在派對上玩得很開心。"
            },
            {
                "sentence": "Please open the window. It’s very _____.",
                "answer": "hot",
                "choices": ["hot", "cold", "dark", "bright"],
                "translation": "請打開窗戶。這裡很熱。"
            },
            {
                "sentence": "Tom is the _____ student in our class.",
                "answer": "tallest",
                "choices": ["best", "fastest", "tallest", "strongest"],
                "translation": "湯姆是我們班最高的學生。"
            },
            {
                "sentence": "I saw a _____ in the forest yesterday.",
                "answer": "deer",
                "choices": ["bear", "deer", "fox", "wolf"],
                "translation": "我昨天在森林裡看到一隻鹿。"
            },
            {
                "sentence": "Can you _____ me the book?",
                "answer": "pass",
                "choices": ["throw", "give", "pass", "hold"],
                "translation": "你可以把書遞給我嗎？"
            }
        ]

        self.total_questions = len(self.questions)
        self.unasked_indices = list(range(self.total_questions))
        self.score = 0
        self.result_shown = False

        self.option_buttons = []
        for i in range(4):
            btn = Button(pos=(game.WINDOW_WIDTH/2, 250 + i*70), size=(400, 50))
            btn.setClick(lambda i=i: self.check_answer(i))
            self.option_buttons.append(btn)
            self.all_sprites.add(btn)

        menu_button = Button(pos=(game.WINDOW_WIDTH*5/6, game.WINDOW_HEIGHT - 50), size=(100, 50))
        menu_button.setClick(lambda: game.chage_state(Menu_State()))
        self.all_sprites.add(menu_button)

        self.load_question()

    def load_question(self):
        self.result_shown = False
        self.selected_index = None

        if not self.unasked_indices:
            from ..state import Menu_State
            game.chage_state(Menu_State())
            return

        self.question_index = random.choice(self.unasked_indices)
        self.unasked_indices.remove(self.question_index)

        q = self.questions[self.question_index]
        self.sentence = q["sentence"]
        self.answer = q["answer"]
        self.choices = q["choices"]
        self.answer_index = self.choices.index(self.answer)
        self.translation = q["translation"]

    def check_answer(self, selected):
        if not self.result_shown:
            self.selected_index = selected
            if selected == self.answer_index:
                self.score += 1
                self.result_shown = True

    def update(self):
        self.all_sprites.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN and self.result_shown:
                self.load_question()
            

    def render(self):
        font = pg.font.Font(self.font_path, self.font_size)

        game.draw_text(game.window, f"剩餘題數：{len(self.unasked_indices)}", 30, game.WINDOW_WIDTH/2, 20)
        sentence_surface = font.render(self.sentence, True, (255, 255, 255))
        sentence_rect = sentence_surface.get_rect(center=(game.WINDOW_WIDTH/2, 100))
        game.window.blit(sentence_surface, sentence_rect)

        for i, btn in enumerate(self.option_buttons):
            if self.result_shown:
                if i == self.answer_index:
                    color = (0, 200, 0)
                elif i == self.selected_index:
                    color = (200, 0, 0)
                else:
                    color = (100, 100, 100)
            else:
                color = (160, 160, 160)

            rect = btn.rect
            pg.draw.rect(game.window, color, rect, border_radius=8)
            text_surface = font.render(self.choices[i], True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=rect.center)
            game.window.blit(text_surface, text_rect)

        if self.result_shown:
            explanation = f"正解：{self.answer} - {self.translation}"
            exp_surface = font.render(explanation, True, (255, 255, 255))
            exp_rect = exp_surface.get_rect(center=(game.WINDOW_WIDTH/2, 520))
            game.window.blit(exp_surface, exp_rect)

            next_surface = font.render("按任意鍵進入下一題", True, (255, 255, 255))
            next_rect = next_surface.get_rect(center=(game.WINDOW_WIDTH/2, 560))
            game.window.blit(next_surface, next_rect)

        self.all_sprites.draw(game.window)