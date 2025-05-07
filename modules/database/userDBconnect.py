import sqlite3
import os

class UserDB:
    def __init__(self, db_path="user_data/users.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def create_user(self, user_name, user_id = None):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user_info (user_id, user_name) VALUES (?,?);",(user_id, user_name,))
                conn.commit()
                print(f"user {user_name} created.")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to create user: {e}")
        return None
    
    def get_user_info(self, user_id, column = None):
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
            return None
    
    def update_user_info(self, user_id: int, **kwargs):
        """
        更新 user_info 表中指定 user_id 的欄位。\n
        例如：update_user_info(1, exp=150, daily_draws=4)\n
        valid_columns = {"user_name", "last_played", "total_play_time", "daily_draws", "exp", "level"}\n
        """
        if not kwargs:
            print("[WARN] No fields to update.")
            return
        valid_columns = {"user_name", "last_played", "total_play_time", "daily_draws", "exp", "level"}
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
        將一張新卡牌加入使用者的 card_collection，如果尚未擁有該卡牌。
        """
        try:
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
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to add card to user: {e}")
        





        
    
