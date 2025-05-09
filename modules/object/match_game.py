import pygame as pg
import random
import game
from ..manager.font_manager import Font_Manager
from .match_card import Match_Card
from .card import Card
from ..database import VocabularyDB
from ..manager import Event_Manager
from ..object import Group



class Match_Game:
    """配對遊戲物件。

    管理配對小遊戲的物件

    Attributes:
        __first_chosen_card (Card): 第一個被選取的卡片
        __second_chosen_card (Card): 第二個被選取的卡片
        __pending_wrong_time (int):  配對錯誤而將卡片翻回去背面的tick時間(預設等待 800 ms)
        __pending_right_time (int):  配對成功而將卡片移動的tick時間(預設等待 800 ms)
        __pending_finish_time (int): 遊戲結束重製前等待的tick時間(預設等待 1000 ms)
        __blue_turn (bool): 是否為藍方回合
        __blue_score (int): 藍方分數
        __red_score (int): 紅方分數
        __blue_background_color (tuple): 藍方回合背景顏色
        __red_background_color (tuple): 紅方回合背景顏色
        __card_sprites (pg.sprite.LayeredUpdates): 所有卡片群組
        __paired_cards (pg.sprite.LayeredUpdates): 配對成功卡片群組
        __layer (int): 繪畫圖層, 當新的配對出現則加一, 使其顯示在最上層
    """

    def __init__(self, cols:int=5, rows:int=4, pos:tuple=(0,0), col_spacing:int=270, row_spacing:int=200):
        total_card_width = (cols-1) * col_spacing
        total_card_height = (rows-1) * row_spacing
        top_left = pos[0]-total_card_width//2, pos[1]-total_card_height//2

        grid = [[(top_left[0] + c * col_spacing, top_left[1] + r * row_spacing) for c in range(cols)] for r in range(rows)]
        self.__first_chosen_card = None
        self.__second_chosen_card = None
        self.__pending_wrong_time = None
        self.__pending_right_time = None
        self.__pending_finish_time = None
        self.__blue_turn = True
        self.__blue_score = 0
        self.__red_score = 0
        self.__blue_background_color = (50,50,120)
        self.__red_background_color = (120,50,50)
        self.__all_cards = Group()
        self.__paired_cards = Group()
        self.__display_cards = Group()
        self.__blue_display_y = 300
        self.__red_display_y = 300
        self.__layer = 0

        words = self.__getWords((cols*rows / 2).__ceil__())
        random.shuffle(words)
        i = 0
        for row in grid:
            for pos in row:
                card = Match_Card(pos=pos, scale=1.5, word=words[i])
                i += 1
                self.__all_cards.add(card, layer=0)

        self.__ori_background_color = game.background_color
        game.background_color = (50,50,100)

    def __del__(self):
        game.background_color = self.__ori_background_color


    def handle_event(self):
        for event in game.event_list:
            if event.type == Event_Manager.EVENT_MATCH_CARD_FLIP:
                card = event.dict.get('card', None)
                if card == None:
                    print("Match_Game.handle_event: event.dict has no 'card' key")
                    return
                if not card.get_show_back():
                    card.can_flip = False
                    if self.__first_chosen_card == None:
                        self.__first_chosen_card = card
                    else:
                        self.__second_chosen_card = card
        self.__all_cards.handle_event()
        # 反向遍歷，先處理後加入的 sprite（最上層）
        for sprite in reversed(self.__display_cards.sprites()):
            sprite.handle_event()

    def update(self):
        self.__all_cards.update()
        self.__display_cards.update()
        current_time = pg.time.get_ticks()

        # 卡片配對錯誤，等待800ms後，翻到卡背
        if self.__pending_wrong_time is not None:
            if current_time >= self.__pending_wrong_time:
                self.__pending_wrong_time = None
                self.__first_chosen_card.can_flip = True
                self.__second_chosen_card.can_flip = True
                self.__first_chosen_card.flip()
                self.__second_chosen_card.flip()
                self.__first_chosen_card = None
                self.__second_chosen_card = None
                self.__set_all_card_flip(True)
                self.__change_player_turn()
            return
        
        # 卡片配對成功，等待800ms後，移動至旁邊並對玩家加分
        if self.__pending_right_time is not None:
            if current_time >= self.__pending_right_time:
                self.__pending_right_time = None
                self.__paired_cards.add(self.__first_chosen_card)
                self.__paired_cards.add(self.__second_chosen_card)
                self.__layer += 1
                self.__all_cards.change_layer(self.__first_chosen_card, self.__layer)
                self.__all_cards.change_layer(self.__second_chosen_card, self.__layer)
                self.__first_chosen_card.setWiggle()
                self.__second_chosen_card.setWiggle()
                word = ''
                if self.__blue_turn:
                    self.__blue_score += 1
                    if(self.__first_chosen_card.get_word()[1] == 'eng'):
                        word = self.__first_chosen_card.get_word()[0]
                        self.__first_chosen_card.moveTo((-300, 300), 1)
                        self.__second_chosen_card.moveTo((-300, 500), 1)
                    else:
                        word = self.__second_chosen_card.get_word()[0]
                        self.__second_chosen_card.moveTo((-300, 300), 1)
                        self.__first_chosen_card.moveTo((-300, 500), 1)
                else:
                    self.__red_score += 1
                    if(self.__first_chosen_card.get_word()[1] == 'eng'):
                        word = self.__first_chosen_card.get_word()[0]
                        self.__first_chosen_card.moveTo((game.CANVAS_WIDTH+300, 300), 1)
                        self.__second_chosen_card.moveTo((game.CANVAS_WIDTH+300, 500), 1)
                    else:
                        word = self.__second_chosen_card.get_word()[0]
                        self.__second_chosen_card.moveTo((game.CANVAS_WIDTH+300, 300), 1)
                        self.__first_chosen_card.moveTo((game.CANVAS_WIDTH+300, 500), 1)
                self.__first_chosen_card = None
                self.__second_chosen_card = None
                self.__set_all_card_flip(True)
                self.__summon_display_card(self.__blue_turn, word)
            return
        
        # 所有卡片配對完成，結算勝者並跳出遊戲(會先等待上面的800ms跑完才過來這邊，但總體等待時間依然為設置的時間)
        if self.__pending_finish_time is not None:
            if current_time >= self.__pending_finish_time:
                self.__pending_finish_time = None
                winner = ''
                if self.__blue_score > self.__red_score:
                    winner = '藍方'
                elif self.__red_score > self.__blue_score:
                    winner = '紅方'
                else:
                    winner = '大家都'
                self.__paired_cards.empty()
                pg.event.post(pg.event.Event(Event_Manager.EVENT_MATCH_GAME_FINISH, {'winner': winner}))
            return

        # 選擇兩張卡片翻開後，如果配對成功，則放入__correct_cards中鎖定(不能再次翻開)
        if self.__first_chosen_card and self.__second_chosen_card:
            first_word = self.__first_chosen_card.get_word()[0]
            second_word = self.__second_chosen_card.get_word()[0]
            if (self.__ans.get(first_word) == second_word) or (self.__ans.get(second_word) == first_word):
                self.__pending_right_time = current_time + 800
                self.__set_all_card_flip(False)
            else:
                self.__pending_wrong_time = current_time + 800
                self.__set_all_card_flip(False)

        if len(self.__paired_cards) == len(self.__all_cards):
            self.__pending_finish_time = current_time + 1000


    def render(self):
        if self.__blue_turn:
            blue_color = (240,240,50)
            red_color = (255,255,255)
        else:
            blue_color = (255,255,255)
            red_color = (240,240,50)
        Font_Manager.draw_text(game.canvas, "藍方:"+str(self.__blue_score)+"分", 60, game.CANVAS_WIDTH/2 - 400, 100, blue_color)
        Font_Manager.draw_text(game.canvas, "紅方:"+str(self.__red_score)+"分", 60, game.CANVAS_WIDTH/2 + 400, 100, red_color)
        self.__all_cards.draw(game.canvas)
        self.__display_cards.draw(game.canvas)
    
    def __getWords(self, n) -> list:
        db = VocabularyDB()
        words = db.find_vocabulary(column='Vocabulary', length=random.randrange(5,8))
        random_words = [(word['Vocabulary'], 'eng') for word in random.sample(words, n)]
        random_words_trans = [db.find_vocabulary(vocabulary=word[0])[0]['Translation'] for word in random_words]
        random_words_trans = [(chinese.split(';')[0].split(',')[0], 'chi') for chinese in random_words_trans]
        self.__ans = {eng[0]: chi[0] for eng, chi in zip(random_words, random_words_trans)}

        mixed_words = random_words + random_words_trans
        return mixed_words
    
    def __set_all_card_flip(self, can_flip):
        for card in self.__all_cards:
            if card not in self.__paired_cards:
                card.can_flip = can_flip

    def __change_player_turn(self):
        self.__blue_turn = not self.__blue_turn
        if self.__blue_turn:
            game.background_color = self.__blue_background_color
        else:
            game.background_color = self.__red_background_color

    def __summon_display_card(self, blue_turn, word):
        db = VocabularyDB()
        id = db.find_vocabulary(vocabulary=word)[0].get('ID', None)        
        card = None
        if blue_turn:
            card = Card((-500, self.__blue_display_y), 2, id)
            card.moveTo((140, self.__blue_display_y), 0.5)
            self.__blue_display_y += 100
        else:
            card = Card((game.CANVAS_WIDTH+500, self.__red_display_y), 2, id)
            card.moveTo((game.CANVAS_WIDTH-165, self.__red_display_y), 0.5)
            self.__red_display_y += 100
        self.__display_cards.add(card)