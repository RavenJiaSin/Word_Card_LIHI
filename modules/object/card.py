import pygame as pg
from .button import Button
from ..manager import Image_Manager
from ..manager import Font_Manager
from modules.database import VocabularyDB

class Card(Button):
    """卡片物件。繼承自Button。

    由於不同頁面可能需要的卡片功能不同，在創建時呼叫`setClick()`可以自定義。

    Attributes:
        __id (str): 卡片id。    
        __data (map): 卡片的資料。 
        __show_eng (bool): 是否顯示英文   
        __show_chi (bool): 是否顯示中文   
    """

    def __init__(self, pos=(0,0), scale:float=1, id:str='1003_card', show_eng:bool=True, show_chi:bool=True):
        db = VocabularyDB()
        self.__id = id
        tmp = db.find_vocabulary(id=id)
        self.__data = {}
        if len(tmp) != 1:
            print(f'Card id matches {len(tmp)} vocabulary')
        else:
            self.__data = db.find_vocabulary(id=id)[0]
        self.__show_eng = show_eng
        self.__show_chi = show_chi
            
        super().__init__(pos=pos, scale=scale, img=Image_Manager.get('card_template'))
        self.setClick(lambda:print('Clicked Card:', self.__id))
        self.__set_image()

    def __set_image(self):

        # 先取得卡片模板    
        card_img = self.image.copy()

        # 將自身圖片清空
        self.image.fill((0,0,0,0)) 
        
        surfs = []
        font_size = int(12*self.scale)
        # 先畫卡片背景
        background = Image_Manager.get('card_background')
        img_surf = pg.transform.smoothscale(background, (background.get_width()*self.scale, background.get_width()*self.scale))
        img_rect = img_surf.get_rect(center=(self.width/2, 95*self.scale))
        surfs.append((img_surf, img_rect))
        
        # 再畫單字圖片
        try:
            db = VocabularyDB()
            tmp = Image_Manager.get_from_path(db.get_image(self.__data['ID']))
            width = tmp.get_width()
            height = tmp.get_height()
            img_surf = pg.transform.smoothscale(tmp, (95*self.scale, height*95/width*self.scale)) 
            img_rect = img_surf.get_rect(center=(self.width/2, 98*self.scale))
            surfs.append((img_surf, img_rect)) 
        except:
            ...

        # 再畫卡片模板
        surfs.append((card_img, card_img.get_rect()))
        
        white_color = (219, 215, 205)
        black_color = (36,36,36)

        # 畫英文
        if self.__show_eng:
            word_surf = Font_Manager.get_text_surface(self.__data.get('Vocabulary', 'None'), font_size, black_color)
            if not self.__show_chi:
                word_rect = word_surf.get_rect(center=(self.width/2,36*self.scale))
            else:
                word_rect = word_surf.get_rect(center=(self.width/2,29*self.scale))
            surfs.append((word_surf, word_rect))

        # 畫中文
        if self.__show_chi:
            ch_word_surf = Font_Manager.get_text_surface(self.__data.get('Translation', '無').split(';')[0].split(',')[0], font_size, black_color)
            if not self.__show_eng:
                ch_word_rect = ch_word_surf.get_rect(center=(self.width/2,36*self.scale))
            else:
                ch_word_rect = ch_word_surf.get_rect(center=(self.width/2,44*self.scale))
            surfs.append((ch_word_surf, ch_word_rect))

        # 畫熟練度(目前hard code為100)
        prof_surf = Font_Manager.get_text_surface('100', font_size, white_color)
        prof_rect = prof_surf.get_rect(center=(25*self.scale, 14*self.scale))
        surfs.append((prof_surf, prof_rect))

        # 畫詞性
        pof_surf = Font_Manager.get_text_surface(self.__data.get('Part_of_speech', 'error'), font_size, white_color)
        pof_rect = pof_surf.get_rect(center=(87*self.scale, 14*self.scale))
        surfs.append((pof_surf, pof_rect))

        # 更新image
        self.image.blits(surfs) 

    def get_id(self) -> str:
        return self.__id
    
    def get_data(self) -> dict:
        return self.__data
