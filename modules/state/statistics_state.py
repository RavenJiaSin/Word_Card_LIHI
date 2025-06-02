import pygame as pg
import game
import datetime
import sqlite3

# 設定 matplotlib 不啟用 GUI 後端
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import io
from PIL import Image
from collections import defaultdict

from .state import State
from ..object import Group, Text_Button, Confirm_Quit_Object, card
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
        cur.execute("SELECT streak_days, total_time, level FROM user_info WHERE user_id = ?", (self.user_id,))
        user_info = cur.fetchone()
        streak_day = user_info[0] if user_info else 0
        play_count = user_info[1] if user_info else 0
        player_level = user_info[2] if user_info else 0

        # card_collection
  # 從 answer_log 統計答題正確與錯誤總數
        cur.execute("SELECT is_correct FROM answer_log WHERE user_id = ?", (self.user_id,))
        rows = cur.fetchall()

        correct_total = sum(1 for (is_correct,) in rows if is_correct == 1)
        wrong_total = sum(1 for (is_correct,) in rows if is_correct == 0)
        total = correct_total + wrong_total
        total_accuracy = round((correct_total / total) * 100, 1) if total > 0 else 0

        # 建立 card_stats: 每個 voc_id 的 correct / wrong / total 統計
        cur.execute("SELECT voc_id, is_correct FROM answer_log WHERE user_id = ?", (self.user_id,))
        rows = cur.fetchall()

        card_stats_dict = defaultdict(lambda: {"correct": 0, "wrong": 0})
        for raw_voc_id, is_correct in rows:
            voc_id = raw_voc_id.split('_', 1)[1] if '_' in raw_voc_id else raw_voc_id
            if is_correct == 1:
                card_stats_dict[voc_id]["correct"] += 1
            else:
                card_stats_dict[voc_id]["wrong"] += 1

        card_stats = []
        for voc_id, counts in card_stats_dict.items():
            total_select = counts["correct"] + counts["wrong"]
            card_stats.append({
                "voc_id": voc_id,
                "correct": counts["correct"],
                "wrong": counts["wrong"],
                "total": total_select
            })

        # 統計最常答錯與答題最多的 top3
        # 過濾掉沒有答錯過的卡片
        wrong_cards = [c for c in card_stats if c["wrong"] > 0]
        most_wrong = max(wrong_cards, key=lambda x: x["wrong"], default=None)
        top3_cards = sorted(card_stats, key=lambda x: x["total"], reverse=True)[:3]


        conn.close()

        # 區塊一：總覽
        self.overview_title = "總覽"
        self.overview_text = [
            f"玩家等級：{player_level}",
            f"練功坊遊玩次數：{play_count}",
            f"累計答題數：{total}",
            f"答對 / 答錯：{correct_total} / {wrong_total}",
            f"整體正確率：{total_accuracy}%",
            f"連續登入天數：{streak_day} 天"
        ]
        self.overview_pos = (500, 160)

        # 區塊二：卡牌統計
        self.card_title = "卡牌統計"
        self.card_text = []

        self.card_text.append(f"最常答錯卡牌：")
        if most_wrong:
            self.card_text.append(
                f"  - {most_wrong['voc_id']}: {most_wrong['correct']}/{most_wrong['wrong']}（共{most_wrong['total']}次）"
            )
        else:
            self.card_text.append("  - 無資料")

        self.card_text.append("卡牌答題 Top 3：")
        self.card_text += [
            f"  - {c['voc_id']}: {c['correct']}/{c['wrong']}（共{c['total']}次）"
            for c in top3_cards
        ]
        self.card_pos = (1350, 160)

        # 區塊三：每日正確率圖表
        labels, values = self.get_weekly_accuracy()
        self.accuracy_chart = self.create_line_chart(labels, values)
        
        # 區塊四：每日新增卡牌圖表（暫位資料）
        labels_new, values_new = self.get_weekly_new_cards()
        self.new_card_chart = self.create_line_chart(labels_new, values_new, title="每日獲得卡牌數", ylabel="卡牌數")

    def get_weekly_accuracy(self):
        conn = sqlite3.connect("user_data/users.db")
        cur = conn.cursor()

        today = datetime.date.today()
        days = [(today - datetime.timedelta(days=i)).isoformat() for i in reversed(range(7))]
        stats = defaultdict(lambda: {"correct": 0, "total": 0})

        cur.execute("SELECT is_correct, timestamp FROM answer_log WHERE user_id = ?", (self.user_id,))
        for is_correct, timestamp in cur.fetchall():
            date = timestamp[:10]
            if date in days:
                stats[date]["total"] += 1
                if is_correct:
                    stats[date]["correct"] += 1

        conn.close()

        labels, values = [], []
        for d in days:
            correct = stats[d]["correct"]
            total = stats[d]["total"]
            acc = round((correct / total) * 100, 1) if total > 0 else 0
            labels.append(d[5:])  # MM-DD
            values.append(acc)
        return labels, values

    def create_line_chart(self, labels, values, title="近七日答題正確率", ylabel="正確率 (%)"):
        import matplotlib.font_manager as fm
        font_path = "res/font/Cubic_11.ttf"  
        chinese_font = fm.FontProperties(fname=font_path)

        fig, ax = plt.subplots(figsize=(6, 3.8))
        fig.subplots_adjust(top=0.85)

        ax.plot(labels, values, marker='o', linewidth=3, color='blue')
        # 顯示每個點的數字
        for i, value in enumerate(values):
            ax.annotate(f"{value}", (labels[i], values[i]),
                        textcoords="offset points", xytext=(0, 12),
                        ha='center', fontproperties=chinese_font, fontsize=12)

        ax.set_ylim(0, 100)
        ax.set_ylabel(ylabel, fontproperties=chinese_font, fontsize=18)
        ax.set_title(title, fontproperties=chinese_font, fontsize=20)
        ax.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format='PNG', dpi=120)
        buf.seek(0)
        plt.close(fig)

        image = Image.open(buf).convert('RGBA')
        mode, size, data = image.mode, image.size, image.tobytes()
        return pg.image.fromstring(data, size, mode)

    def get_weekly_new_cards(self):
        conn = sqlite3.connect("user_data/users.db")
        cur = conn.cursor()

        today = datetime.date.today()
        days = [(today - datetime.timedelta(days=i)).isoformat() for i in reversed(range(7))]
        daily_counts = {day: 0 for day in days}

        cur.execute("SELECT first_acquired_time FROM card_collection WHERE user_id = ?", (self.user_id,))
        for (timestamp,) in cur.fetchall():
            if timestamp:  # 確保不是 None
                date = timestamp[:10]  # 取前10碼 'YYYY-MM-DD'
                if date in daily_counts:
                    daily_counts[date] += 1

        conn.close()

        labels = [d[5:] for d in days]  # 顯示 MM-DD
        values = [daily_counts[d] for d in days]
        return labels, values



    def draw_chart_block(self, image, title, pos):
        x, y = pos
        self.font_manager.draw_text(game.canvas, title, 50, x + 20, y - 60)
        resized = pg.transform.smoothscale(image, (850, 450))
        game.canvas.blit(resized, (x, y))

    
    def draw_block(self, title, text_lines, pos):
        x, y = pos
        spacing = 50
        self.font_manager.draw_text(game.canvas, title, 64, x + 20, y + 20)
        for i, line in enumerate(text_lines):
            font_size = 40 if not line.strip().startswith("-") else 36
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
        if hasattr(self, "accuracy_chart") and self.accuracy_chart:
            resized_chart = pg.transform.smoothscale(self.accuracy_chart, (850, 450))
            chart_pos = (100, 550)
            game.canvas.blit(resized_chart, chart_pos)
            pg.draw.rect(game.canvas, (0, 0, 0), (*chart_pos, 850, 450), width=6)  # 黑色框線

        if hasattr(self, "new_card_chart") and self.new_card_chart:
            resized_new_chart = pg.transform.smoothscale(self.new_card_chart, (850, 450))
            chart_pos = (1000, 550)
            game.canvas.blit(resized_new_chart, chart_pos)
            pg.draw.rect(game.canvas, (0, 0, 0), (*chart_pos, 850, 450), width=6)


        self.confirm_quit_object.render()
