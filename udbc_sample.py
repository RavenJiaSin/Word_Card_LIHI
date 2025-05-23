from modules.database.userDBconnect import UserDB

user_db = UserDB()

# 創建新user
user_db.create_user(user_name = 'test', user_id=4)

# 獲取使用者資訊
print(user_db.get_user_info(user_id=3))

# 更新使用者資訊
# user_db.update_user_info(user_id = 1, level = 1)

# 為user新增一卡牌
# user_db.add_card_to_user(user_id = 1, voc_id='2_adult')

# 查詢使用者有的卡牌資訊
print(user_db.get_card_info(user_id = 1, voc_id = '0_able'))

# 修改user的卡牌資料
# user_db.update_card_info(user_id = 1, voc_id = '0_able', durability = 90)
user_db.update_card_info(user_id = 1, voc_id = '0_able', proficiency = 2)

# 查詢 card_collection 表中耐久度(durability) "<= N" 的卡牌
# print(user_db.get_card_durability_below(user_id = 1, durability = 100))

user_db.add_durability_for_proficiency(user_id=1, proficiency=1, delta = 90)