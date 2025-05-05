import sqlite3
import os

class VocabularyDB:
    def __init__(self, db_path="vocs_data/vocs.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    # 列出資料庫中所有單字及其屬性
    def get_all(self) -> list[dict]:
        try:
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM vocs_raw")
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to fetch all records: {e}")
            return None

    def find_vocabulary(self, column=None, **kwargs) -> list[dict]:
        """
        根據提供的條件從 vocs_raw 查詢資料。\n
        column: 指定要回傳的欄位（例如 'vocabulary'），不指定則為 SELECT *\n
        其餘查詢條件以 key=value 的方式傳入（如 vocabulary="apple", level=2 等）\n
        valid_columns = {"id", "vocabulary", "part_of_speech", "translation", "level"}\n
        valid_pos = {'adj.', '', 'v.', 'adv.', 'prep.', 'conj.', 'n.'}\n
        valid_levels = {1, 2, 3, 4, 5, 6}\n
        filterable_fields = {"id", "vocabulary", "part_of_speech", "level", "length"}\n
        """
        valid_columns = {"id", "vocabulary", "part_of_speech", "translation", "level"}
        valid_pos = {'adj.', '', 'v.', 'adv.', 'prep.', 'conj.', 'n.'}
        valid_levels = {1, 2, 3, 4, 5, 6}

        # 驗證 column 欄位
        if column is not None and column.lower() not in valid_columns:
            raise ValueError(f"Invalid column name: {column}")

        # 建立 SQL 查詢
        select_clause = f"SELECT {column}" if column else "SELECT *"
        query = f"{select_clause} FROM vocs_raw WHERE 1=1"
        params = []

        # 欲支援查詢的欄位清單（白名單）
        filterable_fields = {"id", "vocabulary", "part_of_speech", "level", "length"}

        try:
            for key, value in kwargs.items():
                key=key.lower()
                if key not in filterable_fields:
                    raise ValueError(f"Invalid filter column: {key}")
                
                if key == "part_of_speech" and value not in valid_pos:
                    raise ValueError(f"Invalid part_of_speech: {value}")
                elif key == "level" and value not in valid_levels:
                    raise ValueError(f"Invalid level: {value}")
                elif key == "length":
                    query += " AND LENGTH(vocabulary) = ?"
                    params.append(value)
                else:
                    query += f" AND {key.capitalize()} = ?"
                    params.append(value)

            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except (sqlite3.Error, ValueError) as e:
            print(f"[ERROR] Failed to find vocabulary with conditions: {e}")
            return None


        
    # 查詢欄位合法值
    def get_valid_conditions(self):
        return {
            "database_columns": ["ID", "Vocabulary", "Part_of_speech", "Translation", "Level"],
            "part_of_speech": ['adj.', '', 'v.', 'adv.', 'prep.', 'conj.', 'n.'],
            "level": list(range(1, 7))
        }
    
    # 查詢例句(use ID)
    def get_example_sentences(self, voc_id=None, column=None) -> list[dict]:
        """
        valid_columns = {"example_id", "voc_id", "sentence", "translation"}
        """
        # 定義有效的欄位、詞性和等級
        valid_columns = {"example_id", "voc_id", "sentence", "translation"}
        
        try:
            # 檢查傳入的欄位是否有效
            if column is not None and column not in valid_columns:
                raise ValueError(f"Invalid column name: {column} in {str(valid_columns)}")
            
            # 建立查詢語句和參數
            query = "SELECT * FROM example_sentences WHERE 1=1"
            params = []

            # 如果有提供voc_id，則添加條件
            if voc_id is not None:
                query += " AND voc_id = ?"
                params.append(voc_id)

            # 如果有提供column，則選擇指定的欄位
            if column is not None:
                query = f"SELECT {column} FROM example_sentences WHERE voc_id = ?"
                params = [voc_id]  # 重設參數，只查詢指定的欄位

            # 執行查詢
            with self._connect() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except (sqlite3.Error, ValueError) as e:
            print(f"[ERROR] Failed to find vocabulary with conditions: {e}")
            return None
        
    def get_image(self, voc_id) -> str:
        image_path = f"vocs_data/vocs_img/{voc_id}.png"
        if os.path.exists(image_path):
            return image_path
        else:
            return None

        
    
