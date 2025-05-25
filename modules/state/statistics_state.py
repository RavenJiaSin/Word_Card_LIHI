import pygame as pg
import game
import datetime
import sqlite3
from .state import State
from ..object import Group, Text_Button, Confirm_Quit_Object
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

        self.user_id = 1  # 假設目前登入的是 user_id = 1
        self.user_db = UserDB()
        self.stats = self.get_statistics()
        

    def get_statistics(self):
        conn = sqlite3.connect("user_data/users.db")
        cur = conn.cursor()
        today = datetime.date.today()
        week_start = today - datetime.timedelta(days=6)

        # 1. 練功坊遊玩次數（從 user_info.total_time 為依據）
        cur.execute("SELECT total_time FROM user_info WHERE user_id = ?", (self.user_id,))
        result = cur.fetchone()
        play_count = 1 if result and result[0] > 0 else 0  # 若有遊玩過就算 1 次

        # 2. 練功坊實際完成次數（exp 為 0 表示尚未完成任務）
        cur.execute("SELECT exp FROM user_info WHERE user_id = ?", (self.user_id,))
        result = cur.fetchone()
        complete_count = 1 if result and result[0] > 0 else 0

        # 3. 累積答題數（所有卡牌 correct + wrong 次數總和）
        cur.execute("SELECT SUM(correct_count), SUM(wrong_count) FROM card_collection WHERE user_id = ?", (self.user_id,))
        row = cur.fetchone()
        correct_total = row[0] if row[0] else 0
        wrong_total = row[1] if row[1] else 0
        total = correct_total + wrong_total

        # 4. 總體正確率
        total_accuracy = round((correct_total / total) * 100, 1) if total > 0 else 0

        # 5. 本週正確率（根據 last_review 在本週的卡牌）
        cur.execute("""
            SELECT correct_count, wrong_count FROM card_collection 
            WHERE user_id = ? AND last_review >= ?
        """, (self.user_id, week_start.isoformat()))
        week_correct = 0
        week_total = 0
        for row in cur.fetchall():
            week_correct += row[0]
            week_total += row[0] + row[1]
        week_accuracy = round((week_correct / week_total) * 100, 1) if week_total > 0 else 0


        streak = self.user_db.get_user_info(self.user_id, "streak_days")

        conn.close()
        return {
            "練功坊遊玩次數": play_count,
            "練功坊實際完成次數": complete_count,
            "累積答題數": total,
            "總體正確率": f"{total_accuracy}%",
            "本週正確率": f"{week_accuracy}%",
            "連續登入日數": streak[0]["streak_days"],
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
            Font_Manager.draw_text(game.canvas, text, 36, 200, start_y + i * spacing)
