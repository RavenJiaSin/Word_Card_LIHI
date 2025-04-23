from .button import Button
from ..manager import Image_Manager
from ..manager import Font_Manager

class Card(Button):
    """卡片物件。繼承自Button。

    由於不同頁面可能需要的卡片功能不同，在創建時呼叫`setClick()`可以自定義。

    Attributes:
        __id (str): 卡片名稱。    
    """
    def __init__(self, pos=(0,0), scale:float=1, id:str='Card'):
        self.__id = id
        super().__init__(pos=pos, scale=scale, img=Image_Manager.get('card'))
        self.__set_image()
        self.setClick(lambda:print('Clicked Card:', self.__id))

    def __set_image(self):
        text_surface = Font_Manager.get_text_surface(self.__id, 36, (36,36,36))
        text_rect = text_surface.get_rect(center=(self.width / 2,self.height / 2))
        self.image.blit(text_surface, text_rect)