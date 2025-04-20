import pygame as pg

from .card import Card

class Match_Game:
    def __init__(self, cols:int=8, rows:int=3, top_left:tuple=(300,300), col_spacing:int=200, row_spacing:int=250):
        grid = [[(top_left[0] + c * col_spacing, top_left[1] + r * row_spacing) for c in range(cols)] for r in range(rows)]
        self.card_sprites = pg.sprite.Group()
        
        for row in grid:
            for pos in row:
                card = Card(pos, size=150)
                card.rotate(90)
                self.card_sprites.add(card)


    def update(self):
        pass

    def getGroup(self) -> pg.sprite.Group:
        return self.card_sprites