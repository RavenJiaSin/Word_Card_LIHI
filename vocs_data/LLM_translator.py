
#from modules.vocsDBconnect import VocabularyDB
import ollama
import sqlite3
from deep_translator import GoogleTranslator
import re
from tqdm import tqdm



def fill_empty_translations():
    """
    查詢 translation 欄位為 NULL 或空字串的句子，使用 translate() 補齊
    """
    with sqlite3.connect('vocs_data/vocs.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT example_id, sentence FROM example_sentences WHERE translation IS NULL OR translation = ''")
        rows = cursor.fetchall()

        for example_id, sentence in tqdm(rows, desc="Translating sentences", dynamic_ncols=True):
            if not sentence or sentence.strip() == "":
                continue
            tqdm.write(sentence)
            translation = GoogleTranslator(source='en', target='zh-TW').translate(sentence)
            tqdm.write(translation)
            cursor.execute(
                "UPDATE example_sentences SET translation = ? WHERE example_id = ?",
                (translation, example_id)
            )

        conn.commit()
        print(f"[INFO] Updated {len(rows)} rows with translations.")

if __name__ == '__main__':
    fill_empty_translations()