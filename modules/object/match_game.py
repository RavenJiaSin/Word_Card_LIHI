import pygame as pg

from ..manager import Image_Manager
from .card import Card

class Match_Game:
    def __init__(self, cols:int=6, rows:int=4, top_left:tuple=(340,300), col_spacing:int=250, row_spacing:int=200):
        grid = [[(top_left[0] + c * col_spacing, top_left[1] + r * row_spacing) for c in range(cols)] for r in range(rows)]
        self.__card_sprites = pg.sprite.Group()
        
        self.__angle = 0
        self.__rotate_speed = 2
        for row in grid:
            for pos in row:
                card = Card(pos, size=160, name='tmp_card_back')
                card.stopWiggle()
                self.__card_sprites.add(card)


    def update(self):
        self.__angle += self.__rotate_speed
        if self.__angle >= 90:
            self.__angle = 90

        for card in self.__card_sprites:
            card.rotate(self.__angle)
            card.rect = card.image.get_rect(center=card.rect.center)

    def getGroup(self) -> pg.sprite.Group:
        return self.__card_sprites