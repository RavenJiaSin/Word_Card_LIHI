import pygame as pg
import game
import datetime
import sqlite3
from .state import State
from ..object import Group, Text_Button, Confirm_Quit_Object
from ..manager import Font_Manager, Image_Manager
from modules.database.testDBconnect import TestDB

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

        self.user_id = 1  # 假設目前登入的是 user_id = 1
        self.user_db = TestDB()
        self.stats = self.get_statistics()

    def get_statistics(self):
        conn = sqlite3.connect("user_data/users.db")
        cur = conn.cursor()
        today = datetime.date.today()
        week_start = today - datetime.timedelta(days=6)
        
        # 1. 練功坊統計
        cur.execute("SELECT COUNT(*) FROM train_log WHERE user_id = ?", (self.user_id,))
        play_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM train_log WHERE user_id = ? AND completed = 1", (self.user_id,))
        complete_count = cur.fetchone()[0]

        # 2. 答題總數與正確率
        cur.execute("SELECT SUM(correct_count), SUM(wrong_count) FROM card_collection WHERE user_id = ?", (self.user_id,))
        correct, wrong = cur.fetchone()
        correct = correct or 0
        wrong = wrong or 0
        total = correct + wrong
        total_accuracy = round(correct / total * 100, 1) if total else 0.0

        # 3. 本週正確率
        cur.execute("""
            SELECT COUNT(*), SUM(is_correct)
            FROM answer_log
            WHERE user_id = ? AND DATE(timestamp) >= DATE(?)
        """, (self.user_id, week_start))
        week_total, week_correct = cur.fetchone()
        week_correct = week_correct or 0
        week_accuracy = round(week_correct / week_total * 100, 1) if week_total else 0.0

        # 4. 登入日數與連續登入
        cur.execute("SELECT DISTINCT date FROM login_log WHERE user_id = ?", (self.user_id,))
        dates = [datetime.datetime.strptime(d[0], "%Y-%m-%d").date() for d in cur.fetchall()]
        dates.sort()
        login_days = len(dates)

        # 計算連續登入
        streak = 0
        for i in range(len(dates) - 1, -1, -1):
            if (today - dates[i]).days == streak:
                streak += 1
            else:
                break

        conn.close()
        return {
            "練功坊遊玩次數": play_count,
            "練功坊實際完成次數": complete_count,
            "累積答題數": total,
            "總體正確率": f"{total_accuracy}%",
            "本週正確率": f"{week_accuracy}%",
            "登入日數": login_days,
            "連續登入日數": streak
        }

    def handle_event(self):
        self.all_sprites.handle_event()

    def update(self):
        self.all_sprites.update()

    def render(self):
        Font_Manager.draw_text(game.canvas, "統計", 70, game.CANVAS_WIDTH / 2, 100)
        self.all_sprites.draw(game.canvas)

        # 顯示統計內容
        start_y = 200
        spacing = 50
        for i, (key, value) in enumerate(self.stats.items()):
            text = f"{key}: {value}"
            Font_Manager.draw_text(game.canvas, text, 36, 150, start_y + i * spacing)
