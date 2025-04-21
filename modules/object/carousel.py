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
    def __init__(self, card_count=10, card_size=100, center=(400, 300), radius=400, zoom_factor=0.7, speed=0.005):
        self.center_x, self.center_y = center
        self.radius = radius
        self.zoom_factor = zoom_factor
        self.speed = speed
        self.angle_offset = 0
        self.cards = pg.sprite.Group()

        for i in range(card_count):
            card = Card(pos=center, size=card_size / (1 + zoom_factor), name='test_poker')
            card.stopWiggle()
            self.cards.add(card)

    def rotate(self, delta_angle):
        self.angle_offset += delta_angle
        # 轉一圈就歸零，避免數字太大
        if self.angle_offset >= 2 * math.pi:
            self.angle_offset %= 2 * math.pi

    def __handle_event(self):
        for e in game.event_list:
            if e.type == pg.MOUSEWHEEL:
                self.rotate(e.y * self.speed)

    def update(self):
        self.__handle_event()
        angle_step = 2 * math.pi / len(self.cards.sprites())
        for i, card in enumerate(self.cards.sprites()):
            angle = self.angle_offset + i * angle_step
            scale = 1 + self.zoom_factor * math.cos(angle)
            x = self.center_x + self.radius * math.sin(angle)
            card.transform(x=x, scale=scale)
            card.ori_scale = scale  # 作為按鈕動畫的縮放基準
            card.update()

    def draw(self, surface:pg.Surface):
        # 根據 scale (depth) 排序後再畫
        sorted_cards = sorted(self.cards.sprites(), key=lambda c: c.ori_scale)
        for card in sorted_cards:
             # 根據距離決定透明度
            distance = card.ori_scale ** 4
            opacity = int(distance * 255)
            card.image.set_alpha(opacity)
            surface.blit(card.image, card.rect)