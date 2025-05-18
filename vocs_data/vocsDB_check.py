import google.generativeai as genai
import sqlite3
import re
from tqdm import tqdm
import google.api_core.exceptions
import time
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from modules.database import vocsDBconnect

vocs_db = vocsDBconnect.VocabularyDB()

with open('vocs_data\gemini_api_key', 'r') as api_key_file:
    api_key=api_key_file.readline()

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

def write_example_sentence_to_db(example_id, voc_id, sentence, translation):
    try:
        with vocs_db._connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO example_sentences (example_id, voc_id, sentence, translation)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(example_id) DO UPDATE SET
                    voc_id = excluded.voc_id,
                    sentence = excluded.sentence,
                    translation = excluded.translation
            ''', (example_id, voc_id, sentence, translation))
            conn.commit()
    except sqlite3.Error as e:
        print(f"[ERROR] Failed to insert or update example sentence for example_id {example_id}: {e}")
  

def check_sentences():
    sentences =vocs_db.get_example_sentences()
    error_id = []
    for s in sentences:
        s_id = s['voc_id']
        s_voc = str(vocs_db.find_vocabulary(ID = s_id,column='vocabulary')[0]['Vocabulary'])
        s_pos = str(vocs_db.find_vocabulary(ID = s_id,column='part_of_speech')[0]['Part_of_speech'])
        s_sent = str(s['sentence'])
        ex_id = s['example_id']
        if s_voc.lower() not in s_sent.lower():
            error_id.append(ex_id)
            print(s_id, s_voc, s_pos, s_sent)

            sentence, translation = generate_sentence(s_voc, s_pos)
            write_example_sentence_to_db(ex_id, s_id, sentence, translation)
            print('New:',sentence, translation)
    print(len(error_id))

    


if __name__ == '__main__':
    # error_id_list = check_sentences()
    write_example_sentence_to_db(3682, 'spin', 'I like to spin the top on the table.', '我喜歡在桌上旋轉陀螺。')
    write_example_sentence_to_db(5035, 'horrify', 'Scary movies often horrify young children.', '恐怖電影常常讓小孩感到驚嚇。')
    write_example_sentence_to_db(5044, 'imply', 'These numbers imply a serious problem.', '這些數字暗示了一個嚴重的問題。')
    write_example_sentence_to_db(5076, 'mislead', "Don't mislead people with false information.", '不要用假消息誤導他人。')
    write_example_sentence_to_db(6140, 'ally', 'Small countries often ally to protect their interests.', '小國常常結盟來保護自己的利益。')
    write_example_sentence_to_db(6184, 'cling', 'Wet clothes tend to cling to the body.', '濕衣服容易黏在身上。')
    write_example_sentence_to_db(6519, 'stride', 'Always stride with confidence in a job interview.', '在求職面試中總要自信地大步前行。')
