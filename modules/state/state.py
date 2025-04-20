from abc import ABC, abstractmethod

class State(ABC):
    """基礎抽象狀態類別。繼承自`ABC`(abstract base classes)。

    創建頁面需繼承此類別，並且覆寫`update()`和`render`以描述狀態行為。

    !!新增`handle_event()`提供覆寫

    範例參考`Menu_State`和`Test_State`。
    """

    @abstractmethod
    def handle_event(self):
        ...

    @abstractmethod
    def update(self):
        ...

    @abstractmethod
    def render(self):
        ...