import random
import pygame as pg
import game
from modules.database.userDBconnect import UserDB
from modules.database.vocsDBconnect import VocabularyDB

class Time_Manager():
    voc_db = VocabularyDB()
    user_db = UserDB()

    SECASDAY = 3  # 幾秒當一天
    __last_time = 0

    def __init__(self):
        self.__last_time = pg.time.get_ticks()
        user_cards = self.user_db.get_card_info(user_id = game.USER_ID)

        for card_data in user_cards:
            self.user_db.update_card_info(user_id = game.USER_ID, voc_id = card_data['voc_id'], durability=100, proficiency = random.randint(1,6))
    
    def update(self):
        now = pg.time.get_ticks()
        # 過一天啦
        if now - self.__last_time > self.SECASDAY * 1000:
            self.__last_time = now
            self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=1, delta = -33)
            self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=2, delta = -20)
            self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=3, delta = -12)
            self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=4, delta = -5)
            self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=5, delta = -2)
            self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=6, delta = -1)