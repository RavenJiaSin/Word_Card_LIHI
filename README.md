# WORD_CARD_LIHI

## 分工

### UI

- 開始頁面：莊承儒
- 主頁面：莊承儒
- 練功坊：廖孟宸
- 連連看：許煜祥
- 卡牌庫：戴宏宇
- 卡片設計：張高睿
- 統計資料：

### 其他

- 資料庫：王嘉信


## 1. 環境建置

進入workspace目錄:`\Word_Card_LIHI`

conda：terminal執行:`$ conda create --name <your-env-name> --file requirements_conda.txt`

或

venv：terminal執行:`$ python -m venv <your-env-name> && <your-env-name>/Scripts/activate && pip install -r requirements.txt`

---

## 1.5 執行

打開vscode

`ctrl + shift + p` select interpreter 選擇剛剛建立的環境

執行`python main.py`



## 2. vocs_data
除非有需要更動Database,不然不建議執行或改動其中程式

---

## 3. modules
若在目錄`\Word_Card_LIHI` 可直接使用
```python
from modules.<module_name> import <module_class>
```
---

### 3-1. modules\vocsDBconnect.py

用於簡單存取vocs.db

使用範例請見`vdbc_sample.py`
```python
from modules.vocsDBconnect import VocabularyDB
db = VocabularyDB()
```
method:
1. `.find_vocabulary()`

    return type: list
    ```python
    (method) def find_vocabulary(
        voc: Any | None = None,
        column: Any | None = None,
        part_of_speech: Any | None = None,
        level: Any | None = None
    ) -> Any
    valid_columns = {"ID", "Vocabulary", "Part_of_speech", "Translation", "Level"}
    valid_pos = {'adj.', '', 'v.', 'adv.', 'prep.', 'conj.', 'n.'}
    valid_levels = {1, 2, 3, 4, 5, 6}
    ```
2. `.get_example_sentences()`
    
    return type: list
    ```python
    (method) def get_example_sentences(
        voc_id: Any | None = None,
        column: Any | None = None
    ) -> (list[Any] | None)
    valid_columns = {"example_id", "voc_id", "sentence", "translation"}
    ```
---
