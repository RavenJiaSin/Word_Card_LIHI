import sqlite3

class VocabularyDB:
    def __init__(self, db_path="vocs_data/vocs.db"):
        self.db_path = db_path

    def _connect(self):
        return sqlite3.connect(self.db_path)

    # 列出資料庫中所有單字及其屬性
    def get_all(self):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM vocs_raw")
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to fetch all records: {e}")
            return []

    def find_vocabulary(self, voc=None, column=None, part_of_speech=None, level=None):
        """
        valid_columns = {"ID", "Vocabulary", "Part_of_speech", "Translation", "Level"}\n
        valid_pos = {'adj.', '', 'v.', 'adv.', 'prep.', 'conj.', 'n.'}\n
        valid_levels = {1, 2, 3, 4, 5, 6}
        """
        # 定義有效的欄位、詞性和等級
        valid_columns = {"ID", "Vocabulary", "Part_of_speech", "Translation", "Level"}
        valid_pos = {'adj.', '', 'v.', 'adv.', 'prep.', 'conj.', 'n.'}
        valid_levels = {1, 2, 3, 4, 5, 6}

        try:
            # 檢查傳入的欄位是否有效
            if column is not None and column not in valid_columns:
                raise ValueError(f"Invalid column name: {column} in {str(valid_columns)}")

            # 檢查詞性和等級是否有效
            if part_of_speech is not None and part_of_speech not in valid_pos:
                raise ValueError(f"Invalid part_of_speech: {part_of_speech} in {str(valid_pos)}")

            if level is not None and level not in valid_levels:
                raise ValueError(f"Invalid level: {level} in {str(valid_levels)}")

            # 建立查詢語句和參數
            query = "SELECT * FROM vocs_raw WHERE 1=1"
            params = []

            # 如果有提供voc，則添加條件
            if voc is not None:
                query += " AND Vocabulary = ?"
                params.append(voc)

            # 如果有提供column，則選擇指定的欄位
            if column is not None:
                query = f"SELECT {column} FROM vocs_raw WHERE Vocabulary = ?"
                params = [voc]  # 重設參數，只查詢指定的欄位

            # 如果有提供詞性，則添加條件
            if part_of_speech is not None:
                query += " AND Part_of_speech = ?"
                params.append(part_of_speech)

            # 如果有提供等級，則添加條件
            if level is not None:
                query += " AND Level = ?"
                params.append(level)

            # 執行查詢
            with self._connect() as conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                return cursor.fetchall()

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
    def get_example_sentences(self, voc_id=None, column=None):
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
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                return cursor.fetchall()
        except (sqlite3.Error, ValueError) as e:
            print(f"[ERROR] Failed to find vocabulary with conditions: {e}")
            return None

        
    
