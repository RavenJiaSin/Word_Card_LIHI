import sqlite3
import os
from modules.database.vocsDBconnect import VocabularyDB



class UserDB:
    def __init__(self, db_path="user_data\\users.db"):
        self.db_path = db_path
        vocs_db = VocabularyDB()
        self.valid_id = [id['ID'] for id in vocs_db.find_vocabulary(column='id')]

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def create_user(self, user_name: str, user_id: int = None):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()

                # 檢查 user_name 是否已存在
                cursor.execute("SELECT user_id FROM user_info WHERE user_name = ?;", (user_name,))
                if cursor.fetchone() is not None:
                    print(f"[INFO] User '{user_name}' already exists. No new user created.")
                    return

                # 若 user_id 為 None，讓 SQLite 自動分配（不指定 user_id 欄位）
                if user_id is None:
                    cursor.execute("INSERT INTO user_info (user_name) VALUES (?);", (user_name,))
                else:
                    cursor.execute("INSERT INTO user_info (user_id, user_name) VALUES (?, ?);", (user_id, user_name))

                conn.commit()
                print(f"[SUCCESS] User '{user_name}' created.")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to create user: {e}")

    
    def get_user_info(self, user_id: int, column: str = None) -> list[dict]:
        """
        valid_columns = {"user_id", "user_name", "total_time", "last_played", "daily_draws", "streak_days", "exp", "level", "joined_time"}
        """
        valid_columns = {"user_id", "user_name", "total_time", "last_played", "daily_draws", "streak_days", "exp", "level", "joined_time"}
        
        try:
            if column is not None and column.lower() not in valid_columns:
                raise ValueError(f"Invalid column name: {column} in {str(valid_columns)}")
            
            query = "SELECT * FROM user_info WHERE 1=1"
            params = []

            # 如果有提供column，則選擇指定的欄位
            if column is not None:
                query = f"SELECT {column} FROM user_info WHERE 1=1"

            # 如果有提供user_id，則添加條件
            if user_id is not None:
                query += " AND user_id = ?"
                params.append(user_id)


            # 執行查詢
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        except (sqlite3.Error, ValueError) as e:
            print(f"[ERROR] Failed to find user info: {e}")
            return []
    
    def update_user_info(self, user_id: int, **kwargs):
        """
        更新 user_info 表中指定 user_id 的欄位。\n
        例如：update_user_info(1, exp=150, daily_draws=4)\n
        valid_columns = {"user_name", "last_played", "total_time", "daily_draws", "exp", "level", "streak_days"}\n
        """
        if not kwargs:
            print("[WARN] No fields to update.")
            return
        valid_columns = {"user_name", "last_played", "total_time", "daily_draws", "exp", "level", "streak_days"}
        for key in kwargs:
            if key not in valid_columns:
                print(f"[ERROR] Invalid column: {key}")
                return
        try:
            with self._connect() as conn:
                cursor = conn.cursor()

                fields = ', '.join([f"{key}=?" for key in kwargs.keys()])
                values = list(kwargs.values())
                values.append(user_id)

                sql = f"UPDATE user_info SET {fields} WHERE user_id=?"
                cursor.execute(sql, values)
                conn.commit()
                print(f"[INFO] Updated user_id={user_id} with {kwargs}")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to update user: {e}")

    def add_card_to_user(self, user_id: int, voc_id: str) -> None:
        """
        將一張新卡牌加入使用者的 card_collection，如果尚未擁有該卡牌。\n
        初始值:"proficiency"=1, "durability"=100, "correct_count"=0, "wrong_count"=0, "time_drawn"=1\n
        """
        try:
            if voc_id not in self.valid_id:
                raise Exception('voc_id invalid')
            with self._connect() as conn:
                cursor = conn.cursor()
                # 檢查使用者是否已擁有這張卡牌
                cursor.execute(
                    "SELECT 1 FROM card_collection WHERE user_id = ? AND voc_id = ?",
                    (user_id, voc_id)
                )
                if cursor.fetchone():
                    print(f"[INFO] User {user_id} already owns card {voc_id}.")
                    return

                # 插入新卡牌資料
                cursor.execute(
                    """
                    INSERT INTO card_collection (user_id, voc_id)
                    VALUES (?, ?)
                    """,
                    (user_id, voc_id)
                )
                conn.commit()
                print(f"[INFO] Card {voc_id} added to user {user_id}.")
        except (sqlite3.Error, Exception) as e:
            print(f"[ERROR] Failed to add card to user: {e}")

    def get_card_info(self, user_id: int = None, voc_id: str = None, column: str = None) -> list[dict]:
        """
        查詢 card_collection 表中指定 user_id, voc_id 的資訊或特定欄位。\n
        例如 print(user_db.get_card_info(user_id = 1, voc_id = '0_able', column = 'correct_count'))\n
        valid_columns = {"card_id", "user_id", "voc_id", "proficiency", "durability", "last_review", "correct_count", "wrong_count", "time_drawn", "first_acquired_time"}\n
        """
        valid_columns = {"card_id", "user_id", "voc_id", "proficiency", "durability", "last_review", "correct_count", "wrong_count", "time_drawn", "first_acquired_time"}
        
        try:
            if column is not None and column.lower() not in valid_columns:
                raise ValueError(f"Invalid column name: {column} in {str(valid_columns)}")
            
            query = "SELECT * FROM card_collection WHERE 1=1"
            params = []

            # 如果有提供column，則選擇指定的欄位
            if column is not None:
                query = f"SELECT {column} FROM card_collection WHERE 1=1"

            # 如果有提供user_id，則添加條件
            if user_id is not None:
                query += " AND user_id = ?"
                params.append(user_id)
            
            # 如果有提供voc_id，則添加條件
            if voc_id is not None:
                query += " AND voc_id = ?"
                params.append(voc_id)


            # 執行查詢
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        
        except (sqlite3.Error, ValueError) as e:
            print(f"[ERROR] Failed to find card info: {e}")
            return []
        
    def get_card_durability_below(self, user_id: int, durability: int) -> list[dict]:
        """
        查詢 card_collection 表中耐久度(durability) "<= N" 的卡牌。\n
        例如 print(user_db.get_card_info(user_id = 1, durability = 5))\n
        """
        try:
            query = "SELECT * FROM card_collection WHERE user_id = ? AND durability <= ?"
            params = (user_id, durability)
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except (sqlite3.Error, ValueError) as e:
            print(f"[ERROR] Failed to find card which durability below {durability}: {e}")
            return []


    
    def update_card_info(self, user_id: int, voc_id: str, **kwargs):
        """
        更新 card_collection 表中指定 user_id, voc_id 的欄位。\n
        例如：update_card_info(1, 0_able, correct_count=2)\n
        valid_columns = {"proficiency", "durability", "last_review", "correct_count", "wrong_count", "time_drawn"}\n
        """
        if not kwargs:
            print("[WARN] No fields to update.")
            return
        valid_columns = {"proficiency", "durability", "last_review", "correct_count", "wrong_count", "time_drawn"}
        for key in kwargs:
            if key not in valid_columns:
                print(f"[ERROR] Invalid column: {key}")
                return
        try:
            with self._connect() as conn:
                cursor = conn.cursor()

                # 先確認該使用者是否擁有這張卡
                cursor.execute(
                    "SELECT 1 FROM card_collection WHERE user_id = ? AND voc_id = ?",
                    (user_id, voc_id)
                )
                if not cursor.fetchone():
                    print(f"[WARN] User {user_id} does not own card {voc_id}. Update aborted.")
                    return

                # 組合 SQL 更新語句
                fields = ', '.join([f"{key}=?" for key in kwargs])
                values = list(kwargs.values()) + [user_id, voc_id]
                sql = f"UPDATE card_collection SET {fields} WHERE user_id = ? AND voc_id = ?"

                cursor.execute(sql, values)
                conn.commit()
                print(f"[INFO] Updated card {voc_id} for user {user_id}: {kwargs}")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to update user: {e}")

    def add_durability_for_proficiency(self, user_id: int, proficiency: int, delta: int):
        """
        更新 card_collection 表中指定 user_id, proficiency 的 durability\n
        durability 最小為 0，最大為 100\n
        """
        try:
            if proficiency > 6 or proficiency < 1:
                raise Exception('invalid proficiency')

            with self._connect() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    UPDATE card_collection
                    SET durability = 
                        CASE 
                            WHEN durability + ? < 0 THEN 0
                            WHEN durability + ? > 100 THEN 100
                            ELSE durability + ?
                        END
                    WHERE user_id = ? AND proficiency = ?
                    """,
                    (delta, delta, delta, user_id, proficiency)
                )

                conn.commit()

                if cursor.rowcount == 0:
                    print(f"[WARN] No durability updated — no matching record?")
                else:
                    print(f"[INFO] Updated {user_id}'s cards durability by {delta} (bounded 0~100) where proficiency = {proficiency}")

        except (sqlite3.Error, Exception) as e:
            print(f"[ERROR] Failed to update durability: {e}")

    def log_answer(self, user_id: int, voc_id: str, is_correct: bool):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO answer_log (user_id, voc_id, is_correct)
                    VALUES (?, ?, ?)
                ''', (user_id, voc_id, int(is_correct)))
                conn.commit()
                print(f"[INFO] Logged answer: user={user_id}, voc={voc_id}, correct={is_correct}")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to log answer: {e}")

    def get_daily_cards(self, user_id: int) -> list[dict]:
        """
        取得所有每日卡牌\n
        ex:[{'id': 1, 'user_id': 1, 'voc_id': '0_able'}, {'id': 2, 'user_id': 1, 'voc_id': '1_above'}]
        """
        try:                
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM daily_cards WHERE user_id = ?
                """, (user_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[ERROR] Failed to get daily cards: {e}")
            return []

    def add_daily_cards(self, user_id: int, voc_id: str):
        """
        新增一張每日卡牌
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                # 先檢查是否已存在該筆資料
                cursor.execute("""
                    SELECT 1 FROM daily_cards WHERE user_id = ? AND voc_id = ?
                """, (user_id, voc_id))
                if cursor.fetchone() is not None:
                    print(f"[WARN] daily_card already exists for user_id={user_id}, voc_id={voc_id}")
                    return
                # 若不存在則插入
                cursor.execute("""
                    INSERT INTO daily_cards (user_id, voc_id) VALUES (?, ?)
                """, (user_id, voc_id))
                conn.commit()
            print(f"[INFO] Add {voc_id} to daily_card of user {user_id}")
        except Exception as e:
            print(f"[ERROR] Failed to add daily card: {e}")

    def clear_daily_cards(self, user_id: int):
        """
        清空所有每日卡牌
        """
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM daily_cards WHERE user_id = ?
                """, (user_id,))
                conn.commit()
                
                # 重設 autoincrement（SQLite語法）
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='daily_cards'")
                conn.commit()
            print(f"[INFO] daily cards cleared")
        except Exception as e:
            print(f"[ERROR] Failed to clear daily cards: {e}")





        





        
    
