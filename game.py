import pygame as pg
from modules.state import State, Start_State
from modules.manager import font_map
from modules.manager import Event_Manager

FPS = 60

FULLSCREEN = True
MOUSE_SCALE = 1 if FULLSCREEN else 1.5
CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080

deltaTick = 0
canvas =  pg.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
event_list = None
background_color = (30,30,30)

def change_state(state:State):
    pg.event.post(pg.event.Event(Event_Manager.EVENT_CHANGE_STATE, {"state":state}))

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
        self.__window_width = 1920 if FULLSCREEN else 1280
        self.__window_height = 1080 if FULLSCREEN else 720
        self.__window_flag = (pg.FULLSCREEN | pg.SCALED) if FULLSCREEN else 0
        self.__window = pg.display.set_mode((self.__window_width,self.__window_height),self.__window_flag)
    def run(self):
        global deltaTick, event_list
        while self.__isRunning:
            deltaTick = self.__clock.tick(FPS)

            event_list = pg.event.get()
            for e in event_list:
                if e.type == pg.QUIT:
                    self.__isRunning = False
                    break
                if e.type == Event_Manager.EVENT_CHANGE_STATE:
                    self.__state = e.dict["state"]
                    break

            self.__handle_event()
            self.__update()
            self.__render()
            
    def __handle_event(self):
        self.__state.handle_event()

    def __update(self):
        self.__state.update()

    def __render(self):
        global canvas
        canvas.fill(color=background_color)
        self.__state.render()

        scaled_surface = pg.transform.scale(canvas, self.__window.get_size())
        self.__window.blit(scaled_surface, (0, 0))
        pg.display.update()


    def quit(self):
        print('Successfully quit pygame')
        pg.quit()