# WORD_CARD_LIHI

## 1. conda環境建置

進入workspace目錄:`\Word_Card_LIHI`

terminal執行:`$ conda create --name <env-name> --file requirements.txt`

---

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
    ```
2. `.get_example_sentences()`
    
    return type: list
    ```python
    (method) def get_example_sentences(voc_id: Any) -> list[Any]
    ```
---
