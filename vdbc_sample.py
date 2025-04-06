from modules import VocabularyDB

db = VocabularyDB()

# 查詢所有單字
# print(db.get_all())

# 查詢特定單字
# print(db.find_vocabulary("apple", "Part_of_speech"))

# 查詢詞性為動詞，等級為2的單字
# print(db.find_by_conditions(part_of_speech="v.", level=2))

# 查詢只指定詞性（不指定等級）
# print(db.find_by_conditions(part_of_speech="n."))

# 查詢只指定等級（不指定詞性）
# print(db.find_by_conditions(level=1))

# 查詢特定欄位有哪些值(distinct)
# print(db.list_column_values('part_of_speech'))

print(db.get_valid_conditions())