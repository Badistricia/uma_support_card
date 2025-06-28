"""
配置文件
"""
import os
import time
import uuid
import hashlib

# API认证参数
APPKEY = "d053991039404237a44023da011d3e08"
APPSEC = "1a51393c06a667507a1c5851fb7cba22"

# 请求头配置
class HeaderConfig:
    # B站请求头
    HEADERS = {
        'authority': 'api.game.bilibili.com',
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cookie': 'buvid3=76F55CFB-6E77-3109-2BF7-5AD58CC1E68B05746infoc; b_nut=1729597905; _uuid=2C9C39D7-1027C-8BB2-A634-AC1093D95951E04124infoc; rpdid=|(u))RJkkYkY0J\'u~kmY|))ml; LIVE_BUVID=AUTO4817296837234007; hit-dyn-v2=1; buvid_fp_plain=undefined; CURRENT_QUALITY=116; DedeUserID=415471715; DedeUserID__ckMd5=11cbad4fa17ac735; PVID=3; fingerprint=ff9039e8f0b0687db76f43c84ac1411f; buvid_fp=ff9039e8f0b0687db76f43c84ac1411f; buvid4=F2574029-5200-4A41-C5DF-981358FE7A9207043-024102211-AWSt%2FBgXp6pP2OvAnnKOWA%3D%3D; enable_web_push=DISABLE; enable_feed_channel=ENABLE; header_theme_version=OPEN; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; theme-switch-show=SHOWED; SESSDATA=ea322950%2C1766591802%2C39fcb%2A61CjDe79waq79fBlZbW4rQiT7lLy7ZHW0URqzrrJffDpyUnKHBueYLNfbA3aSIDgb4aO8SVjVBNjcwQmJDVkhRQS0zcmh3cnp5cGlVcVVDM2tMaFh5Q2k1N05SQzZJVzZ3QmNhbm9ZaGdBY1RWNGl1dlJPMmctUVZuVDVhdjN0amhlM3FyQnI4ZnV3IIEC; bili_jct=a7045c2b0835698c19e7418802088323; sid=84oh8j20; bsource=search_bing; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTEzNjc1ODMsImlhdCI6MTc1MTEwODMyMywicGx0IjotMX0.cajUqXljbNQFernds1js16NzqP32JPgzslVCqC4ni1I; bili_ticket_expires=1751367523',
        'origin': 'https://game.bilibili.com',
        'referer': 'https://game.bilibili.com/',
        'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0'
    }

    @staticmethod
    def update_cookie(cookie: str):
        """更新Cookie"""
        HeaderConfig.HEADERS['cookie'] = cookie

# API配置
class ApiConfig:
    # 支援卡列表API
    CARDS_API = "https://api.game.bilibili.com/game/player/tools/uma/support_cards"
    # 支援卡详情API
    CARD_DETAIL_API = "https://api.game.bilibili.com/game/player/tools/uma/support_card_detail"

    @staticmethod
    def generate_sign_params() -> dict:
        """生成请求所需的签名参数"""
        ts = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4())
        params = {
            'ts': ts,
            'nonce': nonce,
            'appkey': APPKEY
        }
        
        # 按照参数名排序
        sorted_params = sorted(params.items())
        # 拼接参数
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        # 加上appsec
        sign_string = query_string + APPSEC
        # 计算MD5
        sign = hashlib.md5(sign_string.encode()).hexdigest()
        params['sign'] = sign
        
        return params

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