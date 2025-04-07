import pygame as pg
import game
from .state import State
from ..object import Button

class Menu_State(State):
    """首頁狀態。繼承自`State`。

    在結構子中，創建`all_sprites`(sprite.Group)，以管理所有首頁會出現的`Object`物件，其他頁面都可以參照這個做法。

    覆寫`update()`時，呼叫`all_sprites.update()`，此時會呼叫我們在`Object`中覆寫的`update()`。

    覆寫`render()`時，呼叫`game.draw_text()`，可以寫文字，並且呼叫`all_sprites.draw()`，此時會根據Object中的rect的資訊，畫出Object中的image。

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
    
    """
    def __init__(self):
        from ..state import Test_State # 在這邊import是為了避免circular import

        self.all_sprites = pg.sprite.Group()

        test_button = Button(pos=(game.WINDOW_WIDTH/2,game.WINDOW_HEIGHT/2), size=(80,60))

        test_button.setClick(lambda:game.chage_state(Test_State()))
        self.all_sprites.add(test_button)

        exit_button = Button(pos=(game.WINDOW_WIDTH/2,game.WINDOW_HEIGHT/2+100), size=(80,60))
        exit_button.setClick(lambda:pg.event.post(pg.event.Event(pg.QUIT)))
        self.all_sprites.add(exit_button)

        
    # override
    def update(self):
        self.all_sprites.update()

    # override
    def render(self):
        game.draw_text(game.window, "Menu", 50, game.WINDOW_WIDTH/2, 50)
        self.all_sprites.draw(game.window)