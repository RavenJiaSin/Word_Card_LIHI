import re
from ..database import VocabularyDB
from .object import Object
from ..manager import Image_Manager
from ..manager import Font_Manager

class Card_Info(Object):
    def __init__(self, pos = (0,0), scale = 1, id = ''):
        img = Image_Manager.get('card_info').copy()
        surfs = []
        db = VocabularyDB()
        data = db.get_example_sentences(voc_id=db.find_vocabulary(vocabulary=id)[0]['ID'])[0]
        data_list = ['sentence','translation']
        current_height = 33
        for k in data_list:
            sentence = self.split_text_to_lines(data.get(k, 'None'), 260, 12)
            for s in sentence:
                sentence_surface = Font_Manager.get_text_surface(s, 12, (36,36,36))
                sentence_rect = sentence_surface.get_rect(left=22,top=current_height)
                surfs.append((sentence_surface, sentence_rect))
                current_height += sentence_surface.get_height()
            current_height += 3
            
        img.blits(surfs)
        super().__init__(pos, scale, img)

    def split_text_to_lines(self, text: str, max_width: int, font_size: int) -> list[str]:
        """
        將句子依據字型與最大寬度自動換行，保留單字與標點不被截斷。
        
        Args:
            text: 要顯示的句子 (全中文或全英文)。
            max_width: 每行允許的最大像素寬度。

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
