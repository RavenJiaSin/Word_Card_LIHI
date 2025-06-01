import math
import pygame as pg

from .card import Card
from .button import Button
import game

class Carousel():
    """卡牌輪盤物件。用於 menu state。  
    Parameters:
        card_count (int): 卡牌個數
        card_size (int): 卡牌最大(最靠近時)的尺寸
        center (tuple): 旋轉的圓心位置
        radius (int): 旋轉半徑
        zoom_factor (float): 控制旋轉的縱深
        speed (float): 滾輪的旋轉力道
    """
    def __init__(self, card_scale=2, center=(400, 300), radius=200, zoom_factor=0.4, speed=0.05):
        self.center_x, self.center_y = center
        self.radius = radius
        self.zoom_factor = zoom_factor
        self.speed = speed
        self.angle_offset = 0
        self.cards = pg.sprite.Group()

        for voc_id in game.daily_card_ids:
            card = Card(pos=center, id=voc_id, scale=card_scale / (1 + zoom_factor))
            self.cards.add(card)
        
        self.wheel_event()

    def rotate(self, delta_angle):
        self.angle_offset += delta_angle
        # 轉一圈就歸零，避免數字太大
        if self.angle_offset >= 2 * math.pi:
            self.angle_offset %= 2 * math.pi

    def wheel_event(self):
        angle_step = 2 * math.pi / len(self.cards.sprites())
        for i, card in enumerate(self.cards.sprites()):
            angle = self.angle_offset + i * angle_step
            scale = 1 + self.zoom_factor * math.cos(angle)
            x = self.center_x + self.radius * math.sin(angle)
            card.transform(x=x, scale=scale)
            card.ori_scale = scale  # 作為按鈕動畫的縮放基準


    def handle_event(self):
        for e in game.event_list:
            if e.type == pg.MOUSEWHEEL:
                self.rotate(e.y * self.speed)
                self.wheel_event()
        sorted_cards = sorted(self.cards.sprites(), key=lambda c: c.ori_scale, reverse=True)
        for i, card in enumerate(sorted_cards):
            card.handle_event()

    def update(self):
        sorted_cards = sorted(self.cards.sprites(), key=lambda c: c.ori_scale, reverse=True)
        for i, card in enumerate(sorted_cards):
            card.update()

    def draw(self, surface:pg.Surface):
        # 根據 scale (depth) 排序後再畫
        sorted_cards = sorted(self.cards.sprites(), key=lambda c: c.ori_scale)
        for card in sorted_cards:
            surface.blit(card.image, card.rect)
            # 把 scale 從 [0,2] -> [0,1]
            distance = card.ori_scale / (1 + self.zoom_factor)
            distance **= 2
            # 根據距離決定透明度
            opacity = int((1 - distance) * 255)
            mask = pg.Surface(card.rect.size, pg.SRCALPHA)
            color =  game.background_color + (opacity,)
            mask.fill(color)
            surface.blit(mask, card.rect)