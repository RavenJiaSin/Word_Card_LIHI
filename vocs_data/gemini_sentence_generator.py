import google.generativeai as genai
import sqlite3
import re
from tqdm import tqdm
import sys
import os
import time
import google.api_core.exceptions
import json
# 把根目錄 (WORD_CARD_LIHI) 加入 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.database import vocsDBconnect

db = vocsDBconnect.VocabularyDB()

with open('vocs_data\gemini_api_key', 'r') as api_key_file:
    api_key=api_key_file.readline()

SAVE_FILE = 'vocs_data/processed_ids.json'

def load_processed_ids():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_processed_ids(processed_ids):
    with open(SAVE_FILE, 'w') as f:
        json.dump(list(processed_ids), f)

def generate_sentence(input_word, input_pos):
    prompt = f'''
        Given the English word and its part of speech, generate only one grammatically correct and natural sentence that correctly uses the word in its **base form** (原形) and part of speech. Do not include any explanation or extra text. Ensure the sentence is accurate in meaning and grammatically correct.

        The generated sentence must:
        - Contain the word "{input_word}" exactly as written (i.e., in its base form).
        - Use it according to its part of speech: {input_pos}.
        - Use simple and commonly known English words where possible (except for the given word).

        Surround the English sentence with '==' at the beginning and end, like this: ==Your sentence here==.

        On a new line, provide a Traditional Chinese translation, surrounded by '~~', like this: ~~你的句子翻譯~~.

        Example:
        Input: apple n.
        Output:
        ==I ate an apple yesterday.==
        ~~我昨天吃了一顆蘋果。~~

        Now, generate a sentence using the word "{input_word}" and its part of speech "{input_pos}". Output only in the specified format.
    '''
    genai.configure(api_key = api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    while True:
        try:
            response = model.generate_content(prompt)
            break
        except google.api_core.exceptions.ResourceExhausted as e:
            print("Quota exceeded. Waiting 60 seconds before retrying...")
            time.sleep(60)

    # 擷取英文與翻譯
    match = re.search(r'==(.+?)==.*~~(.+?)~~', response.text, re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    else:
        return None, None

def write_example_sentence_to_db(voc_id, sentence, translation):
    try:
        with db._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO example_sentences (voc_id, sentence, translation)
                VALUES (?, ?, ?)
            ''', (voc_id, sentence, translation))
            conn.commit()
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to insert example sentence for {voc_id}: {e}")    
    

if __name__ == '__main__':

    with db._connect() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS example_sentences (
            example_id INTEGER PRIMARY KEY AUTOINCREMENT,
            voc_id TEXT,
            sentence TEXT,
            translation TEXT,
            FOREIGN KEY (voc_id) REFERENCES vocs_raw(ID)
        )
        ''')
        conn.commit()
    
    processed_ids = load_processed_ids()
    all_rows = db.get_all()

    for row in tqdm(all_rows, desc="Processing...", dynamic_ncols=True):
        voc_id = row['ID']
        if voc_id in processed_ids:
            continue  # 跳過已完成的

        vocabulary = row['Vocabulary']
        part_of_speech = row['Part_of_speech']
        sentence, translation = generate_sentence(vocabulary, part_of_speech)
        write_example_sentence_to_db(voc_id, sentence, translation)
        tqdm.write(f"{vocabulary}: {sentence} | {translation}")

        # 加入成功處理的 ID 並儲存
        processed_ids.add(voc_id)
        save_processed_ids(processed_ids)