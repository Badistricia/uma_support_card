import os

# API 配置
class ApiConfig:
    # bilibili API 密钥 (请替换为您的有效值)
    APPKEY = "d053991039404237a44023da011d3e08"
    APPSEC = "1a51393c06a667507a1c5851fb7cba22"

# 路径配置
class PathConfig:
    # 数据存储路径
    DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
    CARDS_DATA_PATH = os.path.join(DATA_PATH, 'cards_data.json')
    EVENTS_DATA_PATH = os.path.join(DATA_PATH, 'events_data.json')

# 搜索配置
class SearchConfig:
    # 匹配阈值
    SIMILARITY_THRESHOLD = 0.4

# 请求配置
class RequestConfig:
    # API链接
    CARDS_API = "https://api.game.bilibili.com/game/player/tools/uma/support_cards"
    CARD_DETAIL_API = "https://api.game.bilibili.com/game/player/tools/uma/support_card_detail"
    
    # 请求延迟(秒)
    REQUEST_DELAY = 0.5 