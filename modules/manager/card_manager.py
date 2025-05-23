from ..database import UserDB
from ..database import VocabularyDB
import game

class Card_Manager:
    user_db = UserDB()
    @classmethod
    def player_add_card(cls, voc_id:str):
        cls.user_db.add_card_to_user(game.USER_ID, voc_id)
        cls.user_db.update_card_info(game.USER_ID, voc_id, proficiency=1, last_review=None, correct_count=0, wrong_count=0)
    
    @classmethod
    def player_update_card(cls, voc_id:str, proficiency:int=1, last_review:str=None, correct_count:int=0, wrong_count:int=0):
        cls.user_db.update_card_info(game.USER_ID, voc_id, proficiency=proficiency, last_review=last_review, correct_count=correct_count, wrong_count=wrong_count)
