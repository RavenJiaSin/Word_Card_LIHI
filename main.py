import pygame as pg
pg.init()
from game import Game 
if __name__ == '__main__':
    game = Game()
    game.run()
    game.quit()