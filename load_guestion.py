
    # 題目建構
        #1.根據難度選擇隨機抓取4個資料庫中的單字 
        #2.隨機選擇一個單字作為答案
        #3.將答案所對應的例句挖空作為題目
        #4.將剩餘的3個單字作為選項
    def load_question_orig(self,type,level):
        if self.question_count < self.question_num:
            if self.question_count == 0:
                from modules.database import VocabularyDB
                self.question_history = []
                self.choice_history = []
                self.answer_history = []
                self.level = level
                # 載入資料庫中的單字
                self.db = VocabularyDB()
                '''
                self.voc_list = self.db.find_vocabulary(level)
                '''
                self.voc_list=[ ('4401_sack', 'sack', 'n.', '袋;粗布袋', 3), ('4402_sake', 'sake', 'n.', '理由;緣故;利益', 3), 
                                ('4403_saucer', 'saucer', 'n.', '淺碟', 3), ('4404_sausage', 'sausage', 'n.', '香腸,臘腸', 3), 
                                ('4405_saving', 'saving', 'n.', '挽救;節儉,節約;儲金', 3), ('4406_scale', 'scale', 'n.', '尺度;等級;級別', 3), 
                                ('4407_scarecrow', 'scarecrow', 'n.', '稻草人;威嚇物', 3), ('4408_scarf', 'scarf', 'n.', '圍巾', 3)]
            self.IsAnswering = True
            self.question_count += 1
            self.all_sprites.empty()
            self.question = []
            self.result_shown = False
            self.current_title_text="Question "+str(self.question_count)+"/"+str(self.question_num)
            # 隨機選擇4個單字
            self.choice = random.sample(self.voc_list, 4)
            self.choice_history.append(self.choice)
            # 隨機選擇一個單字作為答案
            self.answer_index = random.randint(0, 3)
            self.answer = self.choice[self.answer_index][1]    
            self.answer_history.append(self.answer)
            # 將答案所對應的例句挖空/單字對應翻譯作為題目
            if type==0:#0:單字中翻英 1:單字英翻中 2:例句填空
                self.answer = self.choice[self.answer_index][1]     
                self.question = self.choice[self.answer_index]
                self.current_question_text = self.question[3]
            elif type==1:
                self.answer = self.choice[self.answer_index][3]
                self.question = self.choice[self.answer_index]
                self.current_question_text = self.question[1]
            elif type==2:
                self.answer = self.choice[self.answer_index][1]
                self.question = self.db.get_example_sentences(voc_id=self.choice[self.answer_index][0])[0]
                sentence = self.question['sentence']
                self.current_question_text = sentence.replace(self.answer, "_____")
            self.question_history.append(self.question)
            print(self.question)
            # 顯示選項                
            for i in range(4):
                if type==1:
                    btn = Text_Button(
                    pos=(game.CANVAS_WIDTH // 2-320+640*(i%2), 600 + i//2 * 200), 
                    scale=1,
                    #size=(600, 100), 
                    text=self.choice[i][3], 
                    font_size=70, 
                    
                    )
                    btn.setClick(lambda i=i:self.check_answer(type, self.choice[i][3]))
                else:
                    btn = Text_Button(
                    pos=(game.CANVAS_WIDTH // 2-320+640*(i%2), 600 + i//2 * 200), 
                    scale=1,
                    #size=(600, 100), 
                    text=self.choice[i][1], 
                    font_size=70, 
                    
                    )
                    btn.setClick(lambda i=i:self.check_answer(type, self.choice[i][1]))
                self.all_sprites.add(btn)
        else:
            self.show_result()
            print("Question History",self.question_history)
            print("Choice History",self.choice_history)
            print("Answer History",self.answer_history)