import sqlite3

class VocabularyDB:
    def __init__(self, db_path="../vocs_data/vocs.db"):
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

    # 查詢單字
    def find_vocabulary(self, voc, column=None):
        try:
            with self._connect() as conn:
                cursor = conn.cursor()
                if column is not None:
                    # 僅允許合法欄位
                    valid_columns = {"ID", "Vocabulary", "Part_of_speech", "Translation", "Level"}
                    if column not in valid_columns:
                        raise ValueError(f"Invalid column name: {column}")

                    query = f"SELECT {column} FROM vocs_raw WHERE Vocabulary = ?"
                    cursor.execute(query, (voc,))
                else:
                    cursor.execute("SELECT * FROM vocs_raw WHERE Vocabulary = ?", (voc,))
                return cursor.fetchall()
        except (sqlite3.Error, ValueError) as e:
            print(f"[ERROR] Failed to find vocabulary '{voc}': {e}")
            return []


    # 查詢pos或level
    def find_by_conditions(self, part_of_speech=None, level=None):
        valid_pos = {'adj.', '', 'v.', 'adv.', 'prep.', 'conj.', 'n.'}
        valid_levels = {1, 2, 3, 4, 5, 6}

        try:
            if part_of_speech is not None and part_of_speech not in valid_pos:
                raise ValueError(f"Invalid part_of_speech: {part_of_speech}")

            if level is not None and level not in valid_levels:
                raise ValueError(f"Invalid level: {level}")

            with self._connect() as conn:
                cursor = conn.cursor()
                query = "SELECT * FROM vocs_raw WHERE 1=1"
                params = []

                if part_of_speech is not None:
                    query += " AND Part_of_speech = ?"
                    params.append(part_of_speech)

                if level is not None:
                    query += " AND Level = ?"
                    params.append(level)

                cursor.execute(query, tuple(params))
                return cursor.fetchall()
        except (sqlite3.Error, ValueError) as e:
            print(f"[ERROR] Failed to search with conditions: {e}")
            return []
        
    # 查詢特定欄位有哪些值(distinct)
    def get_valid_conditions(self):
        return {
            "database_columns": ["ID", "Vocabulary", "Part_of_speech", "Translation", "Level"],
            "part_of_speech": ['adj.', '', 'v.', 'adv.', 'prep.', 'conj.', 'n.'],
            "level": list(range(1, 7))
        }

        
    
