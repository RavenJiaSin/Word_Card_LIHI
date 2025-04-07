from .button import Button
    
class Card(Button):
    """卡片物件。繼承自Button。

    由於不同頁面可能需要的卡片功能不同，在創建時呼叫`setClick()`可以自定義。

    Attributes:
        __name (str): 卡片名稱。透過`setName`更改
        __description (str): 卡片描述。透過`setDescription`更改
    
    """
    def __init__(self, pos=(0,0), size:int=50, img=None):
        size = (size,size*1.5)
        super().__init__(pos, size, img)
        self.setClick(lambda:print('Clicked Card'))
        self.setWiggle()
        self.__name = "Card"
        self.description = "This is a description."

    def setName(self, name:str):
        self.__name = name

    def setDescription(self, description:str):
        self.description = description
            