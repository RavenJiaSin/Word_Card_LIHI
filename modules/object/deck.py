import game
from ..object.group import Group
from ..object.card import Card

class Deck():
    # TODO: 看 cards_data 是不是只要傳 Vocabulary 的 string list 就好
    def __init__(self,pos:tuple=(0,0), cards_data:dict=None):
        self.center_x, self.center_y = pos
        self.__cards_data = cards_data
        self.__cards = Group()
        for idx, card_data in enumerate(self.__cards_data):
            card = Card(
                    pos=(self.center_x, self.center_y + idx),
                    scale=1.5,
                    id=card_data['Vocabulary']
                )
            card.can_press = False
            self.__cards.add(card)

    def draw_a_card(self) -> Card:
        '''
        抽掉一張卡
        '''
        card = self.__cards.get_sprite(-1)
        self.__cards.remove(card)
        return card
        
    def is_empty(self):
        return len(self.__cards.sprites()) == 0
    
    def handle_event(self):
        self.__cards.handle_event()

    def update(self):
        self.__cards.update()

    def render(self):
        self.__cards.draw(game.canvas)