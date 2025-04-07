import os
import pygame as pg

img_map = {}
key = 'test_poker'
img_surface = pg.image.load(os.path.join("res/image", key+'.png'))

img_map[key] = img_surface