from modules.database.userDBconnect import UserDB

user_db = UserDB()

# 創建新user
# user_db.create_user(user_name = 'Alice')

# 獲取使用者資訊
# print(user_db.get_user_info(user_id = 1, column = 'user_name'))

# 更新使用者資訊
user_db.update_user_info(user_id = 1, level = 1)

# 為user新增一卡牌
# user_db.add_card_to_user(user_id = 1, voc_id='0_able')

# 
