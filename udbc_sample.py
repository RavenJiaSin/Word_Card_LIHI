from modules.database.userDBconnect import UserDB

user_db = UserDB()

# 創建新user
# user_db.create_user(user_name = 'Alice')

print(user_db.get_user_info(user_id=14, column="user_name"))
