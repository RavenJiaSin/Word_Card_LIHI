import pygame as pg

class Group(pg.sprite.LayeredUpdates):
    def __init__(self, *sprites, **kwargs):
        super().__init__(*sprites, **kwargs)

    def handle_event(self):
        for sprite in self.sprites():
            sprite.handle_event()

            