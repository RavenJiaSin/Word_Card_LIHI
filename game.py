import pygame as pg
from modules.state import State, Start_State
from modules.manager import Font_Manager
from modules.manager import Event_Manager
from modules.manager import Time_Manager
from modules.manager import SFX_Manager
from user_data.user_DBcreator import create_userDB
from modules.database.userDBconnect import UserDB

FPS = 60

FULLSCREEN = True
MOUSE_SCALE = 1 if FULLSCREEN else 1.5
CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080
USER_ID = 1
DAILY_CARD_NUM = 5

deltaTick = 0
canvas =  pg.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
event_list = None
background_color = (100,155,255)
daily_card_ids = []  # 每日卡牌們的id
opened_today_cards = False
user_db=UserDB()

def change_state(state:State):
    pg.event.post(pg.event.Event(Event_Manager.EVENT_CHANGE_STATE, {"state":state}))

class Game:
    def __init__(self):
        # create users.db and create new user if not exist
        create_userDB()
        user_db.create_user(user_name = 'test_user', user_id=1)
        
        self.__isRunning = True
        self.__window_width = 1920 if FULLSCREEN else 1280
        self.__window_height = 1080 if FULLSCREEN else 720
        self.__window_flag = (pg.FULLSCREEN | pg.SCALED) if FULLSCREEN else 0
        self.__window = pg.display.set_mode((self.__window_width,self.__window_height),self.__window_flag)
        self.__clock = pg.time.Clock()
        self.__state = Start_State()
        self.__time_manager = Time_Manager()
        SFX_Manager.init()

    def run(self):
        global deltaTick, event_list
        while self.__isRunning:
            deltaTick = self.__clock.tick(FPS)

            event_list = pg.event.get()
            for e in event_list:
                if ((e.type == pg.QUIT) or
                    (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE)):
                    self.__isRunning = False
                    break
                if e.type == Event_Manager.EVENT_CHANGE_STATE:
                    self.__state = e.dict["state"]
                    break

            self.__handle_event()
            self.__update()
            self.__render()
            
    def __handle_event(self):
        self.__time_manager.handle_event()
        self.__state.handle_event()

    def __update(self):
        # self.__time_manager.update()
        self.__state.update()

    def __render(self):
        global canvas
        canvas.fill(color=background_color)
        self.__state.render()

        scaled_surface = pg.transform.scale(canvas, self.__window.get_size())
        self.__window.blit(scaled_surface, (0, 0))
        pg.display.update()


    def quit(self):
        SFX_Manager.stop_all()
        pg.quit()
        print('Successfully quit pygame')