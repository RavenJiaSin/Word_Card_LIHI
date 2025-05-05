import asyncio
import pygame as pg
from game import Game

async def main():
    pg.init()
    game = Game()
    while game.isRunning:
        game.run()
        await asyncio.sleep(0)
    game.quit()

asyncio.run(main())
