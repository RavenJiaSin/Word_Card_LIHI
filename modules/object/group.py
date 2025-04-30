import pygame as pg

class Group(pg.sprite.LayeredUpdates):
    """群組物件。繼承自`pg.sprite.LayeredUpdates`。
    
    為了新增handle_event而新增的類別

    其餘操作皆和pg.sprite.Group相同

    LayeredUpdates又多了可以操作圖層的功能

    """
    def __init__(self, *sprites, **kwargs):
        super().__init__(*sprites, **kwargs)

    def handle_event(self):
        for sprite in self.sprites():
            sprite.handle_event()

            