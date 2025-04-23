import pygame as pg
from .button import Button
from ..manager import Image_Manager
from ..manager import Font_Manager
from modules.database import VocabularyDB

class Card(Button):
    """卡片物件。繼承自Button。

    由於不同頁面可能需要的卡片功能不同，在創建時呼叫`setClick()`可以自定義。

    Attributes:
        __id (str): 卡片名稱。    
    """

    __black = (36,36,36)
    __grey = (200,200,200)

    def __init__(self, pos=(0,0), scale:float=1, id:str='card'):
        db = VocabularyDB()
        self.__data = db.find_vocabulary(voc=id)[0] # [('922_apple'), 'apple', 'n.', '蘋果', 1]
        try:
            self.__id = self.__data[1]
        except:
            self.__id = 'Not Found'
            
        super().__init__(pos=pos, scale=scale, img=Image_Manager.get('card'))
        self.__set_image()
        self.setClick(lambda:print('Clicked Card:', self.__id))

    def __set_image(self):

        # 先取得卡片模板    
        card_img = self.image.copy() 

        # 將自身圖片清空
        self.image.fill((0,0,0,0)) 
        
        surfs = []
        font_size = int(12*self.scale)

        # 先畫單字圖片
        img_surf = pg.transform.smoothscale(Image_Manager.get(self.__id), (100*self.scale, 100*self.scale)) 
        img_rect = img_surf.get_rect(center=(self.width/2, 75*self.scale))
        surfs.append((img_surf, img_rect)) 

        # 再畫卡片模板
        surfs.append((card_img, card_img.get_rect()))
        
        # 畫單字
        word_surf = Font_Manager.get_text_surface(self.__id, font_size, self.__black)
        word_rect = word_surf.get_rect(center=(self.width/2,27*self.scale))
        surfs.append((word_surf, word_rect))

        # 畫中文翻譯
        ch_word_surf = Font_Manager.get_text_surface(self.__data[3], font_size, self.__grey)
        ch_word_rect = ch_word_surf.get_rect(center=(75*self.scale,13*self.scale))
        surfs.append((ch_word_surf, ch_word_rect))

        # 畫熟練度(目前hard code為99)
        prof_surf = Font_Manager.get_text_surface('99', font_size, self.__black)
        prof_rect = prof_surf.get_rect(center=(22*self.scale, 13*self.scale))
        surfs.append((prof_surf, prof_rect))

        # 畫英文短句描述(目前hard code為描述蘋果)
        sent_surf = Font_Manager.get_text_surface('a round fruit', font_size, self.__black)
        sent_rect = sent_surf.get_rect(center=(self.width/2, 124*self.scale))
        surfs.append((sent_surf, sent_rect))

        # 句子垂直距離
        sent_gap = 15 * self.scale 

        # 畫中文短句描述(目前hard code為描述蘋果)
        ch_sent = '一種圓形的水果,又香又甜好好吃'
        ch_sent = ch_sent.split(',')
        for i, ch in enumerate(ch_sent):
            ch_surf = Font_Manager.get_text_surface(ch, font_size, self.__black)
            ch_rect = ch_surf.get_rect(center=(self.width/2, i*sent_gap + sent_rect.centery+sent_gap))
            surfs.append((ch_surf, ch_rect))

        # 更新image
        self.image.blits(surfs) 

    def get_id(self) -> str:
        return self.__id
