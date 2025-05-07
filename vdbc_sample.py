from modules.database.vocsDBconnect import VocabularyDB
import random

vocs_db = VocabularyDB()

# 查詢所有單字
# print(vocs_db.get_all())


# 查詢特定單字
print(vocs_db.find_vocabulary(id = '922_apple'))

# 查詢特定單字的特定欄位
print(vocs_db.find_vocabulary(vocabulary='bad'))

# 查詢長度為5的單字
# print(vocs_db.find_vocabulary(column='Vocabulary', length=5 ))

# 查詢詞性為動詞，等級為2的單字
# print(vocs_db.find_vocabulary(part_of_speech="v.", level=2))

# 查詢只指定詞性（不指定等級）
# print(vocs_db.find_vocabulary(part_of_speech="n."))

# 查詢只指定等級（不指定詞性）
# print(vocs_db.find_vocabulary(level=1))

# 查詢欄位合法值
# print(vocs_db.get_valid_conditions())

# 查詢例句(use ID)
# print(vocs_db.get_example_sentences(voc_id='0_able', column='translation' ))
# print(vocs_db.get_example_sentences(voc_id='0_able', column='translation' ))

# 查詢圖片路徑:
# print(vocs_db.get_image('0_able'))