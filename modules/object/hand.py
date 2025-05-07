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
        card_interval = width // cards_num
        self.__cards_pos = [(self.center_x - width // 2 + i * card_interval, self.center_y) for i in range(cards_num)]
        # self.__cards_pos = [(200, 200) for i in range(cards_num)]


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
    
    def get_card_at(self, idx) -> Card:
        '''
        回傳第 idx 張手牌，若為空則回傳 None
        '''
        if idx > self.__cards_num - 1 or idx < 0:
            return None
        return self.__cards[idx]
    
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
                card.stopWiggle()
    
    def handle_event(self):
        for card in self.__cards:
            if card != None:
                card.handle_event() 

    def update(self):
        for card in self.__cards:
            if card != None:
                card.update()

    def draw(self, surface:pg.Surface):
        for card in self.__cards:
            if card != None:
                surface.blit(card.image, card.rect)
