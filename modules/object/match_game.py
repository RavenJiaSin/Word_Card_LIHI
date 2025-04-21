import pygame as pg
import random
import game
from .match_card import Match_Card
from modules.database import VocabularyDB
from ..manager import Event_Manager


class Match_Game:
    """配對遊戲物件。

    管理配對小遊戲的物件
    """
    def __init__(self, cols:int=6, rows:int=4, top_left:tuple=(260,270), col_spacing:int=280, row_spacing:int=230):
        grid = [[(top_left[0] + c * col_spacing, top_left[1] + r * row_spacing) for c in range(cols)] for r in range(rows)]
        self.__card_sprites = pg.sprite.Group()
        self.__correct_cards = []

        words = self.__getWords(cols*rows // 2)
        i = 0
        for row in grid:
            for pos in row:
                card = Match_Card(pos, size=160, word=words[i], font_size=25)
                i += 1
                self.__card_sprites.add(card)

        self.__first_chosen_card = None
        self.__second_chosen_card = None
        self.__pending_flip_time = None

        self.__player_turn = True
        game.background_color = (0,0,100)

    def handle_event(self):
        for event in game.event_list:
            if event.type == Event_Manager.EVENT_MATCH_CARD_FLIP:
                card = event.dict['card']
                if not card.get_show_back():
                    card.can_flip = False
                    if self.__first_chosen_card == None:
                        self.__first_chosen_card = card
                    else:
                        self.__second_chosen_card = card

    def update(self):
        current_time = pg.time.get_ticks()

        # 卡片配對錯誤，等待800ms後，翻到卡背
        if self.__pending_flip_time is not None:
            if current_time >= self.__pending_flip_time:
                self.__first_chosen_card.can_flip = True
                self.__second_chosen_card.can_flip = True
                self.__first_chosen_card.flip()
                self.__second_chosen_card.flip()
                self.__first_chosen_card = None
                self.__second_chosen_card = None
                self.__pending_flip_time = None
                self.__set_all_card_flip(True)
                self.__change_player_turn()
            return

        # 選擇兩張卡片翻開後，如果配對成功，則放入__correct_cards中鎖定(不能再次翻開)
        if self.__first_chosen_card and self.__second_chosen_card:
            first_word = self.__first_chosen_card.get_word()
            second_word = self.__second_chosen_card.get_word()
            if (self.__ans.get(first_word) != second_word) and (self.__ans.get(second_word) != first_word):
                self.__pending_flip_time = current_time + 800
                self.__set_all_card_flip(False)
            else:
                self.__first_chosen_card.setWiggle()
                self.__second_chosen_card.setWiggle()
                self.__correct_cards.append(self.__first_chosen_card)
                self.__correct_cards.append(self.__second_chosen_card)
                self.__first_chosen_card = None
                self.__second_chosen_card = None

    def getGroup(self) -> pg.sprite.Group:
        return self.__card_sprites
    
    def __getWords(self, n) -> list:
        db = VocabularyDB()
        words = db.find_vocabulary(column='Vocabulary', length=random.randrange(5,8))
        random_words = [word[0] for word in random.sample(words, n)]
        random_words_trans = [db.find_vocabulary(column='Translation', voc=word)[0][0] for word in random_words]
        random_words_trans = [chinese.split(';')[0] for chinese in random_words_trans]
        self.__ans = dict(zip(random_words, random_words_trans))

        mixed_words = random_words + random_words_trans
        random.shuffle(mixed_words)
        return mixed_words
    
    def __set_all_card_flip(self, can_flip):
        for card in self.__card_sprites:
            if card not in self.__correct_cards:
                card.can_flip = can_flip

    def __change_player_turn(self):
        self.__player_turn = not self.__player_turn
        if self.__player_turn:
            game.background_color = (0,0,100)
        else:
            game.background_color = (100,0,0)