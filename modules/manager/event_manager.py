import pygame as pg

from modules.state import State

class Event_Manager:
    EVENT_MATCH_CARD_FLIP = pg.event.custom_type()
    EVENT_CHANGE_STATE = pg.event.custom_type()