import pygame as pg

class Event_Manager:
    EVENT_MATCH_CARD_FLIP = pg.event.custom_type()
    EVENT_CHANGE_STATE = pg.event.custom_type()
    EVENT_MATCH_GAME_FINISH = pg.event.custom_type()
    EVENT_SHAKE = pg.event.custom_type()