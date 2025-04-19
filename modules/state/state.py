from abc import ABC, abstractmethod

class State(ABC):
    """基礎抽象狀態類別。繼承自`ABC`(abstract base classes)。

    創建頁面需繼承此類別，並且覆寫`update()`和`render`以描述狀態行為。

    範例參考`Menu_State`和`Test_State`。
    """
    @abstractmethod
    def update(self, event_list):
        ...

    @abstractmethod
    def render(self):
        ...