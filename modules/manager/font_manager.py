import os

font_map = {}

path = 'res/font'

key = 'test_font'
font_map[key] = os.path.join(path, key + '.ttf')

key = 'SWEISANSCJKTC-BLACK'
font_map[key] = os.path.join('res/font', key + '.TTF')

key = 'SWEISANSCJKTC-LIGHT'
font_map[key] = os.path.join('res/font', key + '.TTF')

key = 'SWEISANSCJKTC-REGULAR'
font_map[key] = os.path.join('res/font', key + '.TTF')

key = 'SWEISANSCJKTC-THIN'
font_map[key] = os.path.join('res/font', key + '.TTF')