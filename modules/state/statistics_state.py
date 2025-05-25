import pygame as pg
import game
import datetime
import sqlite3
from .state import State
from ..object import Group, Text_Button, Confirm_Quit_Object,card
from ..manager import Font_Manager, Image_Manager
from modules.database.userDBconnect import UserDB

class Statistics_State(State):
    def __init__(self):
        self.name = "Statistics_State"
        self.font_manager = Font_Manager()
        self.image_manager = Image_Manager()
        self.all_sprites = Group()

        from . import Menu_State
        self.confirm_quit_object = Confirm_Quit_Object(lambda: game.change_state(Menu_State()))
        menu_button = Text_Button(pos=(100, 100), text='首頁')
        menu_button.setClick(lambda: self.confirm_quit_object.set_show(True))
        self.all_sprites.add(menu_button)

        self.user_id = 1
        self.user_db = UserDB()
        self.get_statistics_blocks()

    def get_statistics_blocks(self):
        conn = sqlite3.connect("user_data/users.db")
        cur = conn.cursor()

        # user_info
        cur.execute("SELECT total_time, exp FROM user_info WHERE user_id = ?", (self.user_id,))
        user_info = cur.fetchone()
        total_time = user_info[0] if user_info else 0
        exp = user_info[1] if user_info else 0
        play_count = 1 if total_time > 0 else 0
        time_minutes = round(total_time / 60, 1)

        # card_collection
        cur.execute("SELECT voc_id, correct_count, wrong_count FROM card_collection WHERE user_id = ?", (self.user_id,))
        card_rows = cur.fetchall()
        correct_total = wrong_total = 0
        card_stats = []
        for row in card_rows:
            voc_id, correct, wrong = row
            correct_total += correct
            wrong_total += wrong
            card_stats.append({"voc_id": voc_id, "correct": correct, "wrong": wrong, "total": correct + wrong})

        total = correct_total + wrong_total
        total_accuracy = round((correct_total / total) * 100, 1) if total > 0 else 0
        most_wrong = max(card_stats, key=lambda x: x["wrong"], default=None)
        top5_cards = sorted(card_stats, key=lambda x: x["total"], reverse=True)[:5]

        conn.close()

        # 區塊一：總覽
        self.overview_title = "總覽"
        self.overview_text = [
            f"總遊玩次數：{play_count}",
            f"累計答題數：{total}",
            f"答對 / 答錯：{correct_total} / {wrong_total}",
            f"整體正確率：{total_accuracy}%",
            f"遊玩時間：{time_minutes} 分鐘"
        ]
        self.overview_pos = (500, 160)

        # 區塊二：卡牌統計
        self.card_title = "卡牌統計"
        self.card_text = [
            f"最常答錯卡牌：{most_wrong['voc_id'] if most_wrong else '無資料'}",
            f"最常答錯次數：{most_wrong['wrong'] if most_wrong else 0}",
            "卡牌答題 Top 5："
        ] + [
            f"  - {c['voc_id']}: {c['correct']}/{c['wrong']}（共{c['total']}次）"
            for c in top5_cards
        ]
        self.card_pos = (1000, 160)

    def draw_block(self, title, text_lines, pos):
        x, y = pos
        spacing = 50  # 調高間距對應字體放大

        self.font_manager.draw_text(game.canvas, title, 64, x + 20, y + 20)  # 放大區塊標題
        for i, line in enumerate(text_lines):
            font_size = 40 if not line.strip().startswith("-") else 36  # 判斷是否為列表項
            self.font_manager.draw_text(game.canvas, line, font_size, x + 40, y + 100 + i * spacing)


    def handle_event(self):
        self.confirm_quit_object.handle_event()
        self.all_sprites.handle_event()

    def update(self):
        self.confirm_quit_object.update()
        self.all_sprites.update()

    def render(self):
        self.font_manager.draw_text(game.canvas, "統計", 70, game.CANVAS_WIDTH / 2, 80)
        self.all_sprites.draw(game.canvas)

        self.draw_block(self.overview_title, self.overview_text, self.overview_pos)
        self.draw_block(self.card_title, self.card_text, self.card_pos)
        self.confirm_quit_object.render()
