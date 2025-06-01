import random
import pygame as pg
import game
from ..object.group import Group
from ..object.card import Card

class Hand():
    '''
    手牌堆  
    Attributes:
        cards_num (int): 手牌堆應有幾張牌
    '''
    # TODO: 看 cards_data 是不是只要傳 Vocabulary 的 string list 就好
    def __init__(self,pos:tuple=(0,0), width:int=1, cards_num:int=1):
        self.center_x, self.center_y = pos
        self.__cards_num = cards_num  # 幾張手牌
        self.__cards = [None for i in range(cards_num)]  # 為了讓空位存在，所以不用 Group，而是用 List 管理 cards
        card_interval = width // (cards_num - 1)
        self.__cards_pos = [(self.center_x - width // 2 + i * card_interval, self.center_y) for i in range(cards_num)]
        # self.__cards_pos = [(200, 200) for i in range(cards_num)]
        self.__hovered_card_id = -1  # -1 表示沒有 card 被 hover
        self.__already_go_back = [True for i in range(self.__cards_num)]

    def first_empty_slot_pos(self):
        '''
        回傳第一個空缺的position，若無空缺則回傳 False
        '''
        if self.__cards.count(None) == 0:
            return False
        
        else:
            idx = self.__cards.index(None)
            return self.__cards_pos[idx]

    def add_card(self, card:Card):
        '''
        加入一張卡至第一個空缺，若無空缺則回傳 False
        '''
        if self.__cards.count(None) == 0:
            return False
        
        idx = self.__cards.index(None)
        self.__cards[idx] = card
        pos = self.__cards_pos[idx]
        return True
    
    def remove_card_at(self, id):
        self.__cards[id] = None

    def remove_card_by_ID(self, ID:str):
        '''
        移除指定 ID 的 Card，可接受不存在手牌中的 ID
        '''
        for i  in range(len(self.__cards)):
            card = self.__cards[i]
            if card != None and card.get_data()['ID'] == ID:
                self.__cards[i] = None

    def get_card_by_ID(self, ID:str):
        '''
        獲取指定 ID 的 Card，不存在則回傳None
        '''
        for card in self.__cards:
            if card != None and card.get_data()['ID'] == ID:
                return card
        return None

    def get_card_at(self, idx) -> Card:
        '''
        回傳第 idx 張手牌，若為空則回傳 None
        '''
        if idx > self.__cards_num - 1 or idx < 0:
            return None
        return self.__cards[idx]
    def get_a_random_card(self) -> Card:
        '''
        回傳任一張非空的手牌
        '''
        if self.cards_count() <= 0:
            return None
        non_none_card = [card for card in self.__cards if card != None]
        return random.sample(non_none_card, 1)[0]

    def cards_count(self):
        '''
        回傳目前實際有幾張手牌
        '''
        count = 0
        for card in self.__cards:
            if card != None:
                count += 1
        return count
    
    def activate(self):
        '''
        使手牌可互動
        '''
        for card in self.__cards:
            if card != None:
                card.can_press = True

    def deactivate(self):
        '''
        使手牌無法互動
        '''
        for card in self.__cards:
            if card != None:
                card.can_press = False
    
    def handle_event(self):
        for card in reversed(self.__cards):
            if card != None:
                card.handle_event()

    def update(self):
        for i, card in enumerate(reversed(self.__cards)):  # 上層先更新
            i = self.__cards_num - i - 1
            if card != None:
                card.update()
                # hover 動畫
                # 如果不能點擊就不做hover動畫
                if not card.can_press:
                    continue
                # 沒其它上層卡被hover就hover這張，一次只會有一張卡被 hover
                if self.__hovered_card_id < i and card.is_hover: 
                    self.__hovered_card_id = i
                    x, y = self.__cards_pos[i]
                    card.moveTo((x, y - 100), 100, False)
                    self.__already_go_back[i] = False
                # 不是這張被hover就回歸原位，只應在滑鼠離開時觸發一次，不能用exit
                if self.__hovered_card_id != i and not self.__already_go_back[i]:
                    card.moveTo(self.__cards_pos[i], 200, False)
                    self.__already_go_back[i] = True
                # 滑鼠離開當前 hover 的卡片時，讓出被 hover 的機會
                if card.mouse_exit and self.__hovered_card_id == i:
                    self.__hovered_card_id = -1

    def render(self):
        for card in self.__cards:
            if card != None:
                game.canvas.blit(card.image, card.rect)
            #     pg.draw.rect(game.canvas, (255,0,0), card.hit_box, 2)
