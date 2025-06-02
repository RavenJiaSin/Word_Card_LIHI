import pandas as pd
import re
import sqlite3

def create_userDB():
    # 建立 SQLite 資料庫
    conn = sqlite3.connect("user_data\\users.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_info (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL UNIQUE,
        total_time INTEGER DEFAULT 0,
        last_played TEXT,
        daily_draws INTEGER DEFAULT 5,
        streak_days INTEGER DEFAULT 0,
        exp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        joined_time TEXT DEFAULT (datetime('now', 'localtime'))
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS card_collection (
        card_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        voc_id TEXT NOT NULL,
        proficiency INTEGER DEFAULT 1,
        last_review TEXT,
        correct_count INTEGER DEFAULT 0,
        wrong_count INTEGER DEFAULT 0,
        times_drawn INTEGER DEFAULT 1,
        durability INTEGER DEFAULT 100,
        first_acquired_time TEXT DEFAULT (datetime('now', 'localtime')),
        FOREIGN KEY(user_id) REFERENCES user_info(user_id)
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS answer_log ( 
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER NOT NULL, 
        voc_id TEXT NOT NULL, 
        is_correct INTEGER NOT NULL, 
        timestamp TEXT DEFAULT (datetime('now', 'localtime')), 
        FOREIGN KEY (user_id) REFERENCES user_info(user_id) 
    );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS daily_cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        voc_id TEXT
    );
    ''')

    conn.commit()

    

if __name__ == '__main__':
    create_userDB()