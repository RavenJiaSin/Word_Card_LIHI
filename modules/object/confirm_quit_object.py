from typing import Callable
import pygame as pg
import game
from .group import Group
from .text_object import Text_Object
from .text_button import Text_Button 


class Confirm_Quit_Object():
    """確認是否退出頁面的物件

    `func`: 可以用來設置確認按鈕要做的事情

    `set_show()`: 打開這個物件

    `handle_event()`: 執行按鈕、刪除其餘事件

    `update()`: 更新按鈕

    `render()`: 繪製按鈕、製造黑幕
    
    例如: 退回到首頁-> `Confirm_Quit_Object(lambda: game.change_state(Menu_State()))`

    使用須知:

    1. 不能放在 `Group` 中
    2. 直接放在目前頁面的 `handle_event()` 、 `update()` 、 `render()`
    3. 記得呼叫這個物件的 `handle_event()` 、 `update()` 、 `render()`
    4. `handle_event()` 和 `update()` 要放在目前頁面中 `handle_event()` 和 `update()` **最前面**
    5. `render()` 要放在目前頁面中 `render()` **最後面**
    6. 使用 `set_show` 開啟這個物件

    """
    def __init__(self, func:Callable[[], None] = lambda: None):
        self.__is_show = False

        yes_button = Text_Button(pos=(game.CANVAS_WIDTH/2-200, game.CANVAS_HEIGHT/2), text="Yes")
        yes_button.setClick(func)
        no_button = Text_Button(pos=(game.CANVAS_WIDTH/2+200, game.CANVAS_HEIGHT/2), text="No")
        no_button.setClick(lambda: self.set_show(False))
        title_object = Text_Object((game.CANVAS_WIDTH//2, 350), "Are you sure to go back to menu?", 50)

        self.__ui_sprites = Group()
        self.__ui_sprites.add(yes_button)
        self.__ui_sprites.add(no_button)
        self.__ui_sprites.add(title_object)

    # override
    def handle_event(self):
        if self.__is_show:
            self.__ui_sprites.handle_event()
            game.event_list = []

    # override
    def update(self):
        if self.__is_show:
            self.__ui_sprites.update()

    # override
    def render(self):
        if self.__is_show:
            dark_overlay = pg.Surface((game.CANVAS_WIDTH, game.CANVAS_HEIGHT), flags=pg.SRCALPHA) #黑幕頁面
            dark_overlay.fill((0, 0, 0, 200))  # RGBA，最後一個值是透明度（0~255）
            game.canvas.blit(dark_overlay, (0, 0))  # 把暗幕畫上去
            self.__ui_sprites.draw(game.canvas)

    def set_show(self, is_show:bool):
        self.__is_show = is_show