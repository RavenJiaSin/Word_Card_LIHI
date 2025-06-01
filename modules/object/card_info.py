import re
import pygame as pg
import game
from ..database import VocabularyDB
from ..database import UserDB
from .object import Object
from ..manager import Image_Manager
from ..manager import Font_Manager

class Card_Info(Object):
    def __init__(self, pos = (0,0), scale = 1, id = ''):
        img = Image_Manager.get('card_info')
        img = pg.transform.smoothscale(img, (img.get_width()*scale, img.get_height()*scale))
        surfs = []
        db = VocabularyDB()
        sentence_data = db.get_example_sentences(voc_id=id)[0]
        word_data = db.find_vocabulary(id=id)[0]

        # 單字
        voc_surf = Font_Manager.get_text_surface(word_data.get('Vocabulary', 'None'), 24*scale, (36,36,36))
        voc_rect = voc_surf.get_rect(left=55,top=45)
        surfs.append((voc_surf, voc_rect))

        # 詞性跟等級
        pos_surf = Font_Manager.get_text_surface('(' + word_data.get('Part_of_speech', 'None') + ')' + 'level ' + str(word_data.get('Level', 'None')), 12*scale, (36,36,36))
        pos_rect = pos_surf.get_rect(left=voc_rect.right+15,bottom=voc_rect.bottom-12)
        surfs.append((pos_surf, pos_rect))

        # 中文意思
        trans_surf = Font_Manager.get_text_surface(word_data.get('Translation', '無'), 12*scale, (36,36,36))
        trans_rect = trans_surf.get_rect(left=voc_rect.left,top=voc_rect.bottom)
        surfs.append((trans_surf, trans_rect))

        # 例句:
        sentence_title_surf = Font_Manager.get_text_surface('例句：', 12*scale, (36,36,36))
        sentence_title_rect = sentence_title_surf.get_rect(top=trans_rect.bottom+24, left=voc_rect.left)
        surfs.append((sentence_title_surf, sentence_title_rect))

        # 英文例句、中文例句
        sentence_key = ['sentence','translation']
        top = sentence_title_rect.bottom
        for k in sentence_key:
            sentence = self.split_text_to_lines(sentence_data.get(k, 'None'), 260*scale, 12*scale)
            for i, s in enumerate(sentence):
                sentence_surface = Font_Manager.get_text_surface(s, 12*scale, (36,36,36))
                sentence_rect = sentence_surface.get_rect(top=top,left=voc_rect.left+5)
                surfs.append((sentence_surface, sentence_rect))
                top += sentence_rect.height+2
            
        db = UserDB()
        # 熟練度
        prof = db.get_card_info(game.USER_ID, id, column='proficiency')[0]['proficiency']
        prof_surf = Font_Manager.get_text_surface('熟練度 ' + str(prof), 12*scale, (36,36,36))
        prof_rect = prof_surf.get_rect(bottom=img.get_height()-1, centerx = 100)
        surfs.append((prof_surf, prof_rect))

        # 耐久值
        dura = db.get_card_info(game.USER_ID, id, column='durability')[0]['durability']
        dura_surf = Font_Manager.get_text_surface('耐久值 ' + str(dura) + '/100', 12*scale, (36,36,36))
        dura_rect = dura_surf.get_rect(bottom=img.get_height()-1, centerx = img.get_width()/2-24)
        surfs.append((dura_surf, dura_rect))

        # 正確率
        corr = db.get_card_info(game.USER_ID, id, column='correct_count')[0]['correct_count']
        wron = db.get_card_info(game.USER_ID, id, column='wrong_count')[0]['wrong_count']
        print(corr, wron)
        if corr + wron == 0:
            accu = 0
        else:
            accu = corr / (corr + wron)
        accu_surf = Font_Manager.get_text_surface(f'正確率{accu:.1%}', 12*scale, (36,36,36))
        accu_rect = accu_surf.get_rect(bottom=img.get_height()-1, centerx = 760)
        surfs.append((accu_surf, accu_rect))
         

        img.blits(surfs)
        super().__init__(pos, 1, img)


    def split_text_to_lines(self, text: str, max_width: int, font_size: int) -> list[str]:
        """
        將句子依據字型與最大寬度自動換行，保留單字與標點不被截斷。
        
        Args:
            text: 要顯示的句子 (全中文或全英文)。
            max_width: 每行允許的最大像素寬度。
            font_size: 字體大小

        Returns:
            list[str]: 每行字串的 list。
        """

        # 根據語言簡單分辨切詞方式
        is_chinese = re.search(r'[\u4e00-\u9fff]', text)

        # 中文：逐字切（保留標點）
        if is_chinese:
            tokens = list(text)
        else:
            # 英文：單字 + 空格 + 標點
            tokens = re.findall(r'\w+|[.,!?;:\'\"()\[\]{}<>]|[\s]+', text)

        lines = []
        current_line = ''
        for token in tokens:
            test_line = current_line + token
            if Font_Manager.get_font(font_size).size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                if token == ' ':
                    token = ''
                current_line = token

        if current_line:
            lines.append(current_line)

        return lines
