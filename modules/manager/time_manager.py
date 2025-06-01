import math
import random
from datetime import date
import pygame as pg
import game
from modules.database.userDBconnect import UserDB
from modules.database.vocsDBconnect import VocabularyDB
from . import Event_Manager

class Time_Manager():
    voc_db = VocabularyDB()
    user_db = UserDB()

    SECASDAY = 10  # 幾秒當一天
    __last_time = 0

    def __init__(self):

        # real time system
        today = date.today().isoformat()
        last_time = self.user_db.get_user_info(game.USER_ID, 'last_played')[0]['last_played']
        if today != last_time:
            self.start_a_new_day()
            self.user_db.update_user_info(game.USER_ID, last_played=today)

        # vvvvv just for demo vvvvv
        self.start_a_new_day()
        self.__last_time = pg.time.get_ticks()
        user_cards = self.user_db.get_card_info(user_id = game.USER_ID)

        # for card_data in user_cards:
        #     self.user_db.update_card_info(user_id = game.USER_ID, voc_id = card_data['voc_id'], durability=100, proficiency = random.randint(1,6))
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=1, delta = 100)
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=2, delta = 100)
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=3, delta = 100)
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=4, delta = 100)
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=5, delta = 100)
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=6, delta = 100)
        # ^^^^^ just for demo ^^^^^
    
    def update(self):
        # vvvvv just for demo vvvvv
        now = pg.time.get_ticks()
        if now - self.__last_time > self.SECASDAY * 1000:
            self.__last_time = now
            self.start_a_new_day()
        # ^^^^^ just for demo ^^^^^

    def start_a_new_day(self):
        '''
        過一天啦
        '''
        print('A whole new day')
        pg.event.post(pg.event.Event(Event_Manager.EVENT_ANEWDAY))
        self.update_user_durability()
        self.get_new_daily_cards()
        
    def update_user_durability(self):
        # 耐久度下降
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=1, delta = -33)
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=2, delta = -20)
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=3, delta = -12)
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=4, delta = -5)
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=5, delta = -2)
        self.user_db.add_durability_for_proficiency(user_id=game.USER_ID, proficiency=6, delta = -1)

        for forgotten_card in self.user_db.get_card_durability_below(user_id=game.USER_ID, durability=0):
            self.user_db.update_card_info(game.USER_ID, forgotten_card['voc_id'], proficiency=1)

    def get_new_daily_cards(self): # TODO: 這邏輯應該抽到別的地方
        '''
        抽新卡
        '''
        all_voc = self.voc_db.get_all()
        user_voc = self.user_db.get_card_info(user_id=game.USER_ID)

        # 計算總共點數，一張 Level n 的卡 = n 點
        total_point = 0
        for voc in all_voc:
            total_point += voc['Level']

        # 計算使用者點數
        user_point = 0
        for voc in user_voc:
            user_point += self.voc_db.find_vocabulary(id=voc['voc_id'])[0]['Level']
        # print(user_point)

        # 計算使用者等級，將卡牌庫總點數分成6個區間 (1~6)
        point_per_level = total_point // 6
        user_level = user_point // point_per_level + 1

        # 獲取使用者未擁有的卡牌
        all_voc_id = {voc['ID'] for voc in all_voc}
        user_voc_id = {voc['voc_id'] for voc in user_voc}

        have_not_gain_voc_id = all_voc_id - user_voc_id
        
        # 取得未擁有的卡牌，並按level分類
        draw_from_voc = [[] for i in range(6)]
        for i in range(6):
            draw_from_voc[i] = [voc for voc in all_voc if voc['ID'] in have_not_gain_voc_id and voc['Level'] == i+1]

        # 根據使用者等級抽卡
        card_pool = []
        for i in range(1,7):
            # 盡量給接近使用者等級的卡
            level_difference = abs(user_level - i)
            weight = 0
            if level_difference == 0:
                weight = 6
            elif level_difference == 1:
                weight = 1.5
            elif level_difference == 2:
                weight = 0.5
            
            card_pool += random.sample(draw_from_voc[i-1], math.ceil(game.DAILY_CARD_NUM * weight))
        daily_card = random.sample(card_pool, game.DAILY_CARD_NUM)
        daily_card = [voc['ID'] for voc in daily_card]
        game.daily_card_ids = daily_card