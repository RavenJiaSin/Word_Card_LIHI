import pygame as pg
import game
from .state import State
from ..object.card import Card
from ..object import Text_Button
from ..object import Group
from ..object import Confirm_Quit_Object
from ..manager import Font_Manager
from ..manager import Train_Enum


class Train_Result_State(State):
    """結算頁面，繼承自`State`

    顯示答題總覽與各題複習

    Attributes:
        all_sprites (pg.sprite.Group): 管理所有Object物件。
    
    """

    font_overview_lines = Font_Manager.get_font(40)

    def __init__(self, level:int, mode:int, history:dict):
        self.mode = mode
        self.history = history

        ### Flag ###
        
        self.show_each_result = False # 控制一題一題看還是看總覽
        
        ### 數值計算 ###

        # 共幾題
        self.question_num = len(history[Train_Enum.QUESTION])
        # 各題是否正確
        ans = history[Train_Enum.ANSWER]
        sel = history[Train_Enum.SELECTED]
        self.is_correct = [data_ans["ID"] == data_sel["ID"] for data_ans, data_sel in zip(ans, sel)]
        # 共對幾題
        self.score = sum(self.is_correct)

        ### UI ###
        
        self.all_sprites = Group()
        
        # 建立返回首頁按鈕
        from . import Menu_State, Train_Select_Mode_State
        self.confirm_quit_object = Confirm_Quit_Object(lambda:game.change_state(Menu_State()))
        menu_button = Text_Button(pos=(100, 100), text='首頁')
        menu_button.setClick(lambda: self.confirm_quit_object.set_show(True))
        self.all_sprites.add(menu_button)

        self.text = ""  # 顯示主要區域的文字


    def render_overview(self):
        '''
        繪製答題總覽  
        置左顯示題目的中英對照，並根據答對與否改變作答的顏色
        '''
        overview = f'Your Score: {self.score} / {self.question_num}'
        Font_Manager.draw_text(game.canvas, overview, 50, game.CANVAS_WIDTH // 2, 300)
       
        # 畫各題
        font_size = 26 if self.mode == Train_Enum.SENTENCE else 40
        font = Font_Manager.get_font(font_size)
        y = 340
        for i in range(self.question_num):
            x_left = 200  # 置左的位置
            y += int(font.get_linesize() * 1.3)

            # 題目
            text = f'{i+1}. {self.history[Train_Enum.QUESTION][i]}  '
            width = font.size(text)[0]
            Font_Manager.draw_text(game.canvas, text, font_size, x_left + width // 2, y)
            # 是例句填空的話就換行，不然繼續往左寫
            if self.mode == Train_Enum.SENTENCE:
                y += font.get_linesize()
                x_left = 200 + font.size('Q2')[0]
            else:
                x_left += width

            # 答案與選擇
            if self.mode == Train_Enum.CHI2ENG:
                text_ans = f"{self.history[Train_Enum.ANSWER][i]['Vocabulary']}"
                text_sel = f"{self.history[Train_Enum.SELECTED][i]['Vocabulary']}"
            elif self.mode == Train_Enum.ENG2CHI:
                text_ans = f"{self.history[Train_Enum.ANSWER][i]['Translation']} "
                text_sel = f"{self.history[Train_Enum.SELECTED][i]['Translation']}"
            elif self.mode == Train_Enum.SENTENCE:
                text_ans = f"{self.history[Train_Enum.ANSWER][i]['Vocabulary']} {self.history[Train_Enum.ANSWER][i]['Translation']}"
                text_sel = f"{self.history[Train_Enum.SELECTED][i]['Vocabulary']} {self.history[Train_Enum.SELECTED][i]['Translation']}"
            ## 答案
            color = (50, 50, 240)
            width = font.size(text_ans)[0]
            Font_Manager.draw_text(game.canvas, text_ans, font_size, x_left + width // 2, y, color)
            if self.mode == Train_Enum.SENTENCE:
                y += font.get_linesize()
            else:
                x_left += width

            ## 間隔符
            if self.mode != Train_Enum.SENTENCE:
                text_arrow = '  ->  '
                color = (255, 255, 255)
                width = font.size(text_arrow)[0]
                Font_Manager.draw_text(game.canvas, text_arrow, font_size, x_left + width // 2, y, color)
                x_left += width

            ## 選擇
            color = (50, 240, 50) if self.is_correct[i] else (230, 20, 20)
            width = font.size(text_sel)[0]
            Font_Manager.draw_text(game.canvas, text_sel, font_size, x_left + width // 2, y, color)
            x_left += width

    # override
    def handle_event(self):
        self.confirm_quit_object.handle_event()
        self.all_sprites.handle_event()

    # override
    def update(self):
        self.confirm_quit_object.update()
        self.all_sprites.update()

    # override
    def render(self):
        Font_Manager.draw_text(game.canvas, "練功坊", 70, game.CANVAS_WIDTH/2, 100)

        if not self.show_each_result:
            self.render_overview()

        self.all_sprites.draw(game.canvas)

        self.confirm_quit_object.render()
