from modules.database import VocabularyDB
import random

db = VocabularyDB()

# 查詢所有單字
# print(db.get_all())


# 查詢特定單字
# print(db.find_vocabulary(voc='apple'))

# 查詢特定單字的特定欄位
# print(db.find_vocabulary(voc='apple',column='ID'))

# 查詢長度為5的單字
# print(db.find_vocabulary(column='Vocabulary', length=5 ))

# 查詢詞性為動詞，等級為2的單字
# print(db.find_vocabulary(part_of_speech="v.", level=2))

# 查詢只指定詞性（不指定等級）
# print(db.find_vocabulary(part_of_speech="n."))

# 查詢只指定等級（不指定詞性）
# print(db.find_vocabulary(level=1))

# 查詢欄位合法值
# print(db.get_valid_conditions())

# 查詢例句(use ID)
# print(db.get_example_sentences(voc_id='0_able', column='translation' ))

# 查詢圖片路徑:
print(db.get_image('0_able'))