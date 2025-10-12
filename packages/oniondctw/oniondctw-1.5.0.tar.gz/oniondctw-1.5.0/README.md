# 🧅 洋蔥 (Onion)

一個有趣又實用的 Python 套件，收錄洋蔥的各種名言與趣味功能！

## 安裝

```bash
pip install oniondctw
```

## 功能介紹

### 1. 🧅 hello(name) - 洋蔥問候
讓洋蔥向指定的人打招呼！

```python
from onion import hello

print(hello("世界"))  # 🧅 洋蔥向 世界 問好！
print(hello("小明"))  # 🧅 洋蔥向 小明 問好！
```

### 2. 🧅💧 onionify(text) - 洋蔥風格裝飾
用洋蔥的專屬風格包裝你的文字！

```python
from onion import onionify

print(onionify("哈囉"))        # 🧅💧 哈囉 💧🧅
print(onionify("今天天氣真好"))  # 🧅💧 今天天氣真好 💧🧅
```

### 3. 🧅 onion_quote() - 洋蔥語錄
隨機顯示一句洋蔥本人說過的話！收錄洋蔥的經典語錄，每次呼叫都有不同的驚喜。

```python
from onion import onion_quote

onion_quote()  # 隨機顯示一句洋蔥語錄
# 範例輸出：
# 因為只有你是男娘
# 洋蔥女裝
# 太棒了不要跟他們同流合污
# ... 等等
```

### 4. 🧅 onion_wall(count) - 洋蔥名言牆
一次顯示多條洋蔥語錄，用精美的格式排版！讓你被洋蔥的智慧包圍。

```python
from onion import onion_wall

# 顯示 5 條語錄（預設值）
onion_wall()

# 自訂顯示數量
onion_wall(3)  # 顯示 3 條語錄
onion_wall(10) # 顯示全部 10 條語錄

# 範例輸出：
# ==================================================
#                   🧅 洋蔥名言牆 🧅
# ==================================================
# 
# 📌 名言 1:
#    洋蔥女裝
# 
# 📌 名言 2:
#    太棒了不要跟他們同流合污
# ...
# ==================================================
#              ✨ 共展示了 5 條洋蔥的智慧結晶 ✨
# ==================================================
```

### 5. 📦 version - 版本資訊
查看目前套件的版本資訊。

```python
from onion import version, show_info
from onion.utils import show_info

print(version)  # 1.0.0
show_info()     # 顯示完整資訊
```

## 完整範例

```python
from onion import hello, onionify, onion_quote, onion_wall

# 問候
print(hello("Python"))

# 裝飾文字
message = onionify("洋蔥套件真好用！")
print(message)

# 獲得洋蔥的智慧
onion_quote()

# 展示洋蔥名言牆
onion_wall(3)
```

## 系統需求

- Python >= 3.9
- requests

## 作者

作者：YiChen、HCL_2025

## 授權

本專案採用開源授權。

---

🧅 把洋蔥帶進你的程式碼裡！
