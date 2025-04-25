import google.generativeai as genai
import sqlite3
import re
from tqdm import tqdm
import sys
import os
import time
import google.api_core.exceptions
# 把根目錄 (WORD_CARD_LIHI) 加入 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.database import vocsDBconnect

db = vocsDBconnect.VocabularyDB()

with open('vocs_data\gemini_api_key', 'r') as api_key_file:
    api_key=api_key_file.readline()

def generate_sentence(input_word, input_pos):
    prompt = f'''
        Given the English word and its part of speech, generate only one grammatically correct and natural sentence that correctly uses the word in context. Do not include any explanation or extra text. Ensure the sentence is accurate and appropriate in meaning. Surround the generated sentence with '==' at the beginning and end, like this: ==Your sentence here==.

        Try to use simple and commonly used English words in the sentence, except for the given word which must be used correctly according to its part of speech.

        After the English sentence, provide a Traditional Chinese translation on a new line, wrapped with '~~', like this: ~~你的句子翻譯~~.

        Example:
        Input: apple n.
        Output:
        ==I ate an apple yesterday.==
        ~~我昨天吃了一顆蘋果。~~

        Now, generate a sentence using the word {input_word} and its part of speech {input_pos}. Output only in the same format.
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
    
    

if __name__ == '__main__':
    for row in tqdm(db.get_all(), desc="Processing...", dynamic_ncols=True):
        voc_id = row[0]
        vocabulary = row[1]
        part_of_speech = row[2]
        sentence,translate = generate_sentence(vocabulary, part_of_speech)
        
        tqdm.write(f"{vocabulary}: {sentence} | {translate}")