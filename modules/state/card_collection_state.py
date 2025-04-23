import pygame as pg
import game
from .state import State
from ..object import Button
from ..object import Text_Button
from ..object import Card
from functools import partial
from ..manager import Font_Manager

class Card_Collection_State(State):

    def __init__(self):
        from . import Menu_State  # 在這邊import是為了避免circular import
        self.background_cards = pg.sprite.Group()
        self.ui_sprites = pg.sprite.Group()
        self.foreground_card_group = pg.sprite.GroupSingle()
        self.foreground_card = None

        menu_button = Text_Button(pos=(100, 100), scale=1, text='MENU', font_size=20)
        menu_button.setClick(lambda:game.change_state(Menu_State()))
        self.ui_sprites.add(menu_button)

        
        
        for row in range(2):
            for col in range(5):
                card = Card(pos=(360 + col * 300, 360 + row * 300), scale=1)
                card.setClick(partial(self.try_enlarge_card, card))
                self.background_cards.add(card)

    def enlarge_card(self, card):
        self.foreground_card = Card(pos=(game.CANVAS_WIDTH/2, game.CANVAS_HEIGHT/2), scale=3)
        self.foreground_card_group.add(self.foreground_card)

    def try_enlarge_card(self, card):
        if self.foreground_card:
            self.foreground_card_group.empty()
            self.foreground_card = None
        else:
            self.enlarge_card(card)

    # override
    def handle_event(self):
        for event in game.event_list:
            if event.type == pg.MOUSEBUTTONDOWN:
                
                mouse_pos = pg.mouse.get_pos()

                if self.foreground_card:
                    # 如果點的位置不在卡片上，就關掉
                    if not self.foreground_card.rect.collidepoint(event.pos):
                        self.foreground_card_group.empty()
                        self.foreground_card = None

                else:
                # 沒有放大卡 → 檢查是否點到背景卡牌或 UI 按鈕
                    for sprite in self.ui_sprites:
                        if sprite.rect.collidepoint(mouse_pos) and hasattr(sprite, 'onClick'):
                            sprite.onClick()
                            return

                    for card in self.background_cards:
                        if card.rect.collidepoint(mouse_pos) and hasattr(card, 'onClick'):
                            card.onClick()
                            return

    # override
    def update(self):
        self.background_cards.update()
        self.ui_sprites.update()
        if self.foreground_card:
            self.foreground_card.update()

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "Card Collection", 70, game.CANVAS_WIDTH/2 + 50 , 100)
        self.background_cards.draw(game.canvas)  # 背景卡牌
        if self.foreground_card:
            dark_overlay = pg.Surface((game.CANVAS_WIDTH, game.CANVAS_HEIGHT), flags=pg.SRCALPHA) #黑幕頁面，製造聚焦效果
            dark_overlay.fill((0, 0, 0, 180))  # RGBA，最後一個值是透明度（0~255）
            game.canvas.blit(dark_overlay, (0, 0))  # 把暗幕畫上去
            self.foreground_card_group.draw(game.canvas)
        self.ui_sprites.draw(game.canvas)