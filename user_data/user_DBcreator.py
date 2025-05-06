import pandas as pd
import re
import sqlite3

def create_userDB():
    # 建立 SQLite 資料庫
    conn = sqlite3.connect("user_data/users.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_info(
        user_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT NOT NULL UNIQUE,
        total_time    INTEGER DEFAULT 0,            -- 單位：秒或分鐘
        last_played   TEXT,                         -- ISO 格式時間字串
        daily_draws   INTEGER DEFAULT 5,            -- 今日剩餘抽卡次數
        streak_days   INTEGER DEFAULT 0,            -- 連續登入天數
        exp           INTEGER DEFAULT 0,            -- 玩家經驗值
        level         INTEGER DEFAULT 1,            -- 玩家等級
        joined_time   TEXT DEFAULT CURRENT_TIMESTAMP -- 註冊時間
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS card_collection (
        card_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id       INTEGER NOT NULL,
        voc_id        TEXT NOT NULL,
        proficiency   INTEGER DEFAULT 0,             -- 熟練度
        correct_count INTEGER DEFAULT 0,             -- 回答正確次數
        wrong_count   INTEGER DEFAULT 0,             -- 回答錯誤次數
        last_review   TEXT,                          -- 上次複習時間（可用於記憶曲線）
        FOREIGN KEY (user_id) REFERENCES user_info(user_id)
    );
    ''')
    conn.commit()

    

if __name__ == '__main__':
    create_userDB()