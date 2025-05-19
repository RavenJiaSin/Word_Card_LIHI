import pygame as pg
import game
from modules.database.userDBconnect import UserDB
class Time_Manager():
    user_db = UserDB()
    
    SECASDAY = 60  # 幾秒當一天
    last_time = 0

    def __init__(self):
        last_time = pg.time.get_ticks()
    
    def update(self):
        now = pg.time.get_ticks()
        # 過一天啦
        if now - self.base > self.SECASDAY * 1000:
            last_time = now
            self.user_db.add_durability_for_proficiency(user_id=game., proficiency=1, delta = 90)
            