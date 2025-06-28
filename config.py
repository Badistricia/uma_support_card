import os
import time
import uuid
import hashlib

# API认证参数
APPKEY = "d053991039404237a44023da011d3e08"
APPSEC = "1a51393c06a667507a1c5851fb7cba22"

# API配置
class ApiConfig:
    # 支援卡列表API
    CARDS_API = "https://api.game.bilibili.com/game/player/tools/uma/support_cards"
    # 支援卡详情API
    CARD_DETAIL_API = "https://api.game.bilibili.com/game/player/tools/uma/support_card_detail"

# 路径配置
class PathConfig:
    # 数据文件路径
    DATA_PATH = "./data/uma_support_card"
    # 支援卡数据文件
    CARDS_FILE = "cards.json"
    # 支援卡详情数据文件
    DETAILS_FILE = "card_details.json"
    # 上次更新时间文件
    LAST_UPDATE_FILE = "last_update.txt"

# 搜索配置
class SearchConfig:
    # 模糊搜索阈值
    SIMILARITY_THRESHOLD = 0.6
    # 最大返回结果数
    MAX_RESULTS = 5

# 请求配置
class RequestConfig:
    # API链接
    CARDS_API = "https://api.game.bilibili.com/game/player/tools/uma/support_cards"
    CARD_DETAIL_API = "https://api.game.bilibili.com/game/player/tools/uma/support_card_detail"
    
    # 请求延迟(秒)
    REQUEST_DELAY = 0.5

# API 鉴权工具
def generate_auth_params():
    """生成API请求所需的鉴权参数"""
    # 生成时间戳(毫秒)
    ts = str(int(time.time() * 1000))
    
    # 生成随机字符串
    nonce = str(uuid.uuid4())
    
    params = {
        'ts': ts,
        'nonce': nonce,
        'appkey': APPKEY
    }
    return params

def add_sign(params):
    """
    添加签名到参数字典中
    官方签名规则：
    1. 按照key字典序排序
    2. 拼接成 key1=value1&key2=value2&...&key_n=value_n 格式
    3. 在最后拼接上App Secret
    4. 计算MD5作为签名
    """
    # 复制参数，避免修改原始字典
    params_copy = params.copy()
    
    # 按键名升序排序
    sorted_params = sorted(params_copy.items())
    
    # 构造签名字符串：key1=value1&key2=value2...&key_n=value_n
    sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
    
    # 添加appsec
    sign_string = sign_string + APPSEC
    
    # MD5加密
    sign = hashlib.md5(sign_string.encode('utf-8')).hexdigest()
    
    # 添加签名到参数中
    params_copy['sign'] = sign
    
    return params_copy 