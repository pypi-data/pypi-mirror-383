import random

# 洋蔥語錄庫
ONION_QUOTES = [
    "因為只有你是男娘",
    " .洋蔥女裝",
    "那一天的女裝女裝起來",
    "我看到的只有潛在的垃圾訊息發送者，Discord 已屏蔽該訊息。",
    "敲碗洋蔥女裝full ver. ",
    "太棒了不要跟他們同流合污",
    "為什麼妳的屁股會長痘痘？4個步驟重獲光滑美臀！",
    "我的 pigue 開始報 error 了",
    "鈔怎麼甚至還有 user install",
    "總有一天的排程會輪到我婆的"
]

def hello(name="世界"):
    return f"🧅 洋蔥向 {name} 問好！"

def onionify(text):
    """用洋蔥風格包裝文字"""
    return f"🧅💧 {text} 💧🧅"

def onion_quote():
    """洋蔥語錄：隨機顯示一句洋蔥說過的名言"""
    print(random.choice(ONION_QUOTES))

def onion_wall(count=5):
    """洋蔥名言牆：一次顯示多條洋蔥語錄，用漂亮的格式排版
    
    Args:
        count: 要顯示的語錄數量，預設為 5 條
    """
    print("=" * 50)
    print("🧅 洋蔥名言牆 🧅".center(50))
    print("=" * 50)
    
    # 隨機選取不重複的語錄
    selected_quotes = random.sample(ONION_QUOTES, min(count, len(ONION_QUOTES)))
    
    for i, quote in enumerate(selected_quotes, 1):
        print(f"\n📌 名言 {i}:")
        print(f"   {quote}")
    
    print("\n" + "=" * 50)
    print(f"✨ 共展示了 {len(selected_quotes)} 條洋蔥的智慧結晶 ✨".center(50))
    print("=" * 50)
