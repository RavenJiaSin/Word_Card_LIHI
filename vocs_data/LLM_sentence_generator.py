# 執行一次本程式就會新增一個例句到vocs.db裡的example_sentence table

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'modules')))
from vocsDBconnect import VocabularyDB
#from modules.vocsDBconnect import VocabularyDB
import ollama
import sqlite3
import re
from tqdm import tqdm

db = VocabularyDB()

def generate_sentence(input_word, input_pos):
    prompt = f'''
        Given the English word and its part of speech, generate only one sentence that correctly uses the word in context. Do not include any explanation or extra text. Surround the generated sentence with '==' at the beginning and end, like this: ==Your sentence here==.
        
        Example:
        Input: apple n.
        Output: ==I ate an apple yesterday.==

        Now, generate a sentence using the word {input_word} and its part of speech {input_pos}. Output only in the same format."
    '''
    response = ollama.generate(model="llama3",prompt=prompt)
    
    match = re.search(r'==(.+?)==', response["response"])
    if match:
        return match.group(1).strip()
    else:
        return None

def write_example_sentence_to_db(voc_id, sentence):
    try:
        with db._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO example_sentences (voc_id, sentence)
                VALUES (?, ?)
            ''', (voc_id, sentence))
            conn.commit()
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to insert example sentence for {voc_id}: {e}")

if __name__ == '__main__':
    check = input('執行一次本程式就會新增一個例句到vocs.db裡的example_sentence table, 是否要繼續執行(y/n)').lower()
    if check != 'y':exit()
    
    with db._connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS example_sentences (
            example_id INTEGER PRIMARY KEY AUTOINCREMENT,
            voc_id TEXT,
            sentence TEXT,
            FOREIGN KEY (voc_id) REFERENCES vocs_raw(ID)
        )
        ''')
        conn.commit()

    for row in tqdm(db.get_all(), desc="Processing...", dynamic_ncols=True):
        voc_id = row[0]
        vocabulary = row[1]
        part_of_speech = row[2]
        sentence = generate_sentence(vocabulary, part_of_speech)
        
        tqdm.write(f"{vocabulary}: {sentence}")
        write_example_sentence_to_db(voc_id, sentence)
