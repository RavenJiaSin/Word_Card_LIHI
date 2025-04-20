import pygame as pg
from modules.state import State, Menu_State, Start_State
from modules.manager import font_map

FPS = 60

FULLSCREEN = True
WINDOW_WIDTH = 1920 if FULLSCREEN else 1280
WINDOW_HEIGHT = 1080 if FULLSCREEN else 720
WINDOW_FLAG = (pg.FULLSCREEN | pg.SCALED) if FULLSCREEN else 0

EVENT_CHANGE_STATE = pg.event.custom_type()
deltaTick = 0
window = None
canvas =  pg.Surface((1920, 1080))
event_list = None

def chage_state(state:State):
    pg.event.post(pg.event.Event(EVENT_CHANGE_STATE, {"state":state}))

def draw_text(surf, text, size, x, y, font='SWEISANSCJKTC-REGULAR'):
    font = pg.font.Font(font_map[font], size)
    text_surface = font.render(text, True, (200, 200, 200))
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.centery = y
    surf.blit(text_surface, text_rect)

class Game:
    def __init__(self):
        pg.init()
        self.__isRunning = True
        self.__clock = pg.time.Clock()
        self.__state = Start_State()
        global window
        window = pg.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT),WINDOW_FLAG)
    def run(self):
        global deltaTick, event_list
        while self.__isRunning:
            deltaTick = self.__clock.tick(FPS)

            event_list = pg.event.get()
            for e in event_list:
                if e.type == pg.QUIT:
                    self.__isRunning = False
                    break
                if e.type == EVENT_CHANGE_STATE:
                    self.__state = e.dict["state"]
                    break
            self.__update()
            self.__render()
            

    def __update(self):
        self.__state.update()

    def __render(self):
        global window, canvas
        canvas.fill(color=(30,30,30))
        self.__state.render()

        scaled_surface = pg.transform.scale(canvas, window.get_size())
        window.blit(scaled_surface, (0, 0))
        pg.display.update()

    def quit(self):
        print('Successfully quit pygame')
        pg.quit()