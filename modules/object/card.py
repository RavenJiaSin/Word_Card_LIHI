import pygame as pg
from .button import Button
from ..manager import Image_Manager
from ..manager import Font_Manager
from ..database import VocabularyDB
from ..database import UserDB
import game

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
            
        img = self.__get_image(scale)
        super().__init__(pos=pos, scale=1, img=img)
        self.setClick(lambda:print('Clicked Card:', self.__id))

    def __get_image(self, scale) -> pg.surface.Surface:

        # 先取得卡片模板    
        card_template_img = Image_Manager.get('card_template')
        card_template_img = pg.transform.smoothscale(card_template_img, (card_template_img.get_width()*scale, card_template_img.get_height()*scale))

        # 將自身圖片清空
        img = pg.Surface(card_template_img.get_size(), flags=pg.SRCALPHA)
        img.fill((0,0,0,0))
        img_center_x = img.get_rect().centerx
        
        surfs = []
        font_size = int(12*scale)
        # 先畫卡片背景
        background_surf = Image_Manager.get('card_background')
        background_surf = pg.transform.smoothscale(background_surf, (background_surf.get_width()*scale, background_surf.get_width()*scale))
        background_rect = background_surf.get_rect(center=(img_center_x, 95*scale))
        surfs.append((background_surf, background_rect))
        
        # 再畫單字圖片
        try:
            db = VocabularyDB()
            word_img_surf = Image_Manager.get_from_path(db.get_image(self.__data.get('ID', 'None')))
            width = word_img_surf.get_width()
            height = word_img_surf.get_height()
            word_img_surf = pg.transform.smoothscale(word_img_surf, (95*scale, height*95/width*scale)) 
            word_img_rect = word_img_surf.get_rect(center=(img_center_x, 98*scale))
            surfs.append((word_img_surf, word_img_rect)) 
        except:
            print(f'No img found: ID({self.__id})')
            ...

        # 再畫卡片模板
        surfs.append((card_template_img, card_template_img.get_rect()))
        
        white_color = (219, 215, 205)
        black_color = (36,36,36)

        # 畫英文
        if self.__show_eng:
            word_surf = Font_Manager.get_text_surface(self.__data.get('Vocabulary', 'None'), font_size, black_color)
            if not self.__show_chi:
                word_rect = word_surf.get_rect(center=(img_center_x,36*scale))
            else:
                word_rect = word_surf.get_rect(center=(img_center_x,29*scale))
            surfs.append((word_surf, word_rect))

        # 畫中文
        if self.__show_chi:
            ch_word_surf = Font_Manager.get_text_surface(self.__data.get('Translation', '無').split(';')[0].split(',')[0], font_size, black_color)
            if not self.__show_eng:
                ch_word_rect = ch_word_surf.get_rect(center=(img_center_x,36*scale))
            else:
                ch_word_rect = ch_word_surf.get_rect(center=(img_center_x,44*scale))
            surfs.append((ch_word_surf, ch_word_rect))


        userdb = UserDB()
        # 畫熟練度(目前hard code為1)
        if len(userdb.get_card_info(game.USER_ID, self.__data.get('ID', 'None'))) != 0:
            card_info = userdb.get_card_info(game.USER_ID, self.__data.get('ID', 'None'))[0]
        else:
            card_info = {'proficiency': 0, 'last_review': None, 'correct_count': 0, 'wrong_count': 0, 'times_drawn': 1}
        

        prof_surf = Font_Manager.get_text_surface(str(card_info['proficiency']), font_size, white_color)
        prof_rect = prof_surf.get_rect(center=(25*scale, 14*scale))
        surfs.append((prof_surf, prof_rect))

        # 畫詞性
        pof_surf = Font_Manager.get_text_surface(self.__data.get('Part_of_speech', 'error'), font_size, white_color)
        pof_rect = pof_surf.get_rect(center=(87*scale, 14*scale))
        surfs.append((pof_surf, pof_rect))

        # 更新image
        img.blits(surfs) 

        return img

    def get_id(self) -> str:
        return self.__id
    
    def get_data(self) -> dict:
        return self.__data
