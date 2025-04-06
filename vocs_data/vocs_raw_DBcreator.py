import pandas as pd
import re
import sqlite3

def create_vocs_raw():
    # 建立 SQLite 資料庫
    conn = sqlite3.connect("vocs.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vocs_raw (
        ID TEXT PRIMARY KEY,
        Vocabulary TEXT,
        Part_of_speech TEXT,
        Translation TEXT,
        Level INTEGER             
    )
    ''')
    conn.commit()

    id = 0
    for level in range(1,7):
        df = pd.read_excel("senior_7000.xls", sheet_name=level-1, header= None)  # 讀取第一個工作表
        for element in df.loc[:][0]:
            voc = element[:element.index('@')]  
            pos = element[element.index('(')+1:element.index('.')+1] #part of speech
            trans = re.split(r'\.[0-9]+\)',element)[1]
            cursor.execute('''
                INSERT INTO vocs_raw (
                    ID,
                    Vocabulary,
                    Part_of_speech,
                    Translation,
                    Level
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(ID) DO UPDATE SET 
                    Vocabulary = excluded.Vocabulary,
                    Part_of_speech = excluded.Part_of_speech,
                    Translation = excluded.Translation,
                    Level = excluded.Level
                ''', (str(id)+'_'+voc, voc, pos, trans, level))
            id+=1
    conn.commit()
    conn.close()
    print("vocs_raw Done!")

if __name__ == '__main__':
    create_vocs_raw()