import os
import json
import asyncio
import difflib
import urllib.parse
import uuid
import time
import hashlib
import aiohttp
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta

from hoshino import aiorequests, priv, Service, logger
from hoshino.typing import CQEvent
from hoshino.util import filt_message
from . import sv
from .config import ApiConfig, PathConfig, SearchConfig, RequestConfig, generate_auth_params, add_sign, APPKEY, APPSEC, HeaderConfig

# 创建数据目录
os.makedirs(PathConfig.BASE_PATH, exist_ok=True)

# 全局变量
support_cards = []
cards_events = {}

# 事件类型名称映射
EVENT_TYPE_NAMES = {
    'branch_story': '分支剧情',
    'no_branch_story': '普通剧情',
    'after_match_story': '比赛后剧情',
    'continuous_story': '连续剧情',
    'trip_story': '外出剧情'
}

# 数据管理相关函数
def load_data() -> Tuple[Dict, Dict]:
    """加载数据文件"""
    cards_data = {}
    details_data = {}
    
    # 加载支援卡数据
    if os.path.exists(PathConfig.CARDS_DATA_PATH):
        with open(PathConfig.CARDS_DATA_PATH, 'r', encoding='utf-8') as f:
            cards_data = json.load(f)
    
    # 加载详情数据
    if os.path.exists(PathConfig.DETAILS_DATA_PATH):
        with open(PathConfig.DETAILS_DATA_PATH, 'r', encoding='utf-8') as f:
            details_data = json.load(f)
    
    return cards_data, details_data

def save_data(cards_data: Dict, details_data: Dict) -> None:
    """保存数据到文件"""
    # 保存支援卡数据
    with open(PathConfig.CARDS_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(cards_data, f, ensure_ascii=False, indent=2)
    
    # 保存详情数据
    with open(PathConfig.DETAILS_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(details_data, f, ensure_ascii=False, indent=2)
    
    # 更新时间记录
    with open(PathConfig.LAST_UPDATE_PATH, 'w', encoding='utf-8') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# API请求相关函数
async def fetch_support_cards() -> Optional[Dict]:
    """获取支援卡列表"""
    try:
        params = ApiConfig.generate_sign_params()
        
        async with aiohttp.ClientSession(headers=HeaderConfig.HEADERS) as session:
            async with session.get(ApiConfig.CARDS_API, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data['code'] == 0:
                        return data['data']
                    logger.error(f'获取支援卡列表失败: {data["message"]}')
                    return None
                logger.error(f'获取支援卡列表失败: HTTP {resp.status}')
                return None
    except Exception as e:
        logger.error(f'获取支援卡列表异常: {e}')
        return None

async def fetch_support_card_detail(card_id: int) -> Optional[Dict]:
    """获取支援卡详情"""
    try:
        params = ApiConfig.generate_sign_params()
        params['card_id'] = card_id
        
        async with aiohttp.ClientSession(headers=HeaderConfig.HEADERS) as session:
            async with session.get(ApiConfig.CARD_DETAIL_API, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data['code'] == 0:
                        return data['data']
                    logger.error(f'获取支援卡详情失败: {data["message"]}')
                    return None
                logger.error(f'获取支援卡详情失败: HTTP {resp.status}')
                return None
    except Exception as e:
        logger.error(f'获取支援卡详情异常: {e}')
        return None

# 数据更新与处理函数
async def process_card_events(card: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """处理单张卡片的事件数据"""
    card_id = card['card_id']
    card_name = card['name']
    
    # 获取卡片详细信息
    detail = await fetch_support_card_detail(card_id)
    if not detail:
        return card_id, {}
    
    # 整理事件数据
    events = {}
    
    # 处理各种类型的剧情
    for story_type in ['branch_story', 'no_branch_story', 'after_match_story', 
                       'continuous_story', 'trip_story']:
        if story_type in detail and detail[story_type]:
            story_events = []
            for story in detail[story_type]:
                story_events.append({
                    'story_id': story['story_id'],
                    'story_name': story['story_name'],
                    'options': [opt for opt in story['select_value_list']]
                })
            events[story_type] = story_events
    
    return card_id, {
        'card_name': card_name,
        'events': events
    }

async def update_data() -> bool:
    """更新全部协助卡和事件数据"""
    global support_cards, cards_events
    
    # 获取所有协助卡
    card_list = await fetch_support_cards()
    if not card_list:
        return False
    
    support_cards = card_list
    save_data(support_cards, {})
    sv.logger.info(f"已获取到 {len(support_cards)} 张协助卡基础数据")
    
    # 获取每张卡的详细信息及事件
    all_events = {}
    for i, card in enumerate(support_cards):
        sv.logger.info(f"处理第 {i+1}/{len(support_cards)} 张卡: {card['name']}")
        
        card_id, card_data = await process_card_events(card)
        if card_data:
            all_events[card_id] = card_data
        
        # 每次请求之间添加延时，避免请求过于频繁
        await asyncio.sleep(RequestConfig.REQUEST_DELAY)
    
    # 更新全局数据
    cards_events = all_events
    save_data(support_cards, all_events)
    sv.logger.info(f"协助卡事件数据处理完成，共 {len(all_events)} 张卡")
    
    return True

# 测试API鉴权
async def test_api_auth() -> dict:
    """测试API鉴权，返回API响应"""
    try:
        # 生成鉴权参数
        params = generate_auth_params()
        
        # 添加签名
        params = add_sign(params)
        
        # 构造完整URL
        query_string = urllib.parse.urlencode(params)
        full_url = f"{RequestConfig.CARDS_API}?{query_string}"
        
        sv.logger.info(f"测试请求完整URL: {full_url}")
        resp = await aiorequests.get(RequestConfig.CARDS_API, params=params)
        data = await resp.json()
        return data
    except Exception as e:
        sv.logger.error(f"测试API鉴权异常: {e}")
        return {"error": str(e)}

# 查询与格式化函数
def find_events_by_name(event_name: str) -> Optional[List[Dict[str, Any]]]:
    """根据事件名模糊搜索事件"""
    if not event_name or not cards_events:
        return None
        
    found_events = []
    
    for card_id, card_data in cards_events.items():
        card_name = card_data['card_name']
        events = card_data['events']
        
        for event_type, event_list in events.items():
            for event in event_list:
                # 使用difflib进行模糊匹配
                similarity = difflib.SequenceMatcher(None, event_name, event['story_name']).ratio()
                
                # 如果相似度大于阈值或者关键词直接包含在事件名中
                if similarity > SearchConfig.SIMILARITY_THRESHOLD or event_name in event['story_name']:
                    found_events.append({
                        'card_id': card_id,
                        'card_name': card_name,
                        'story_name': event['story_name'],
                        'event_type': event_type,
                        'options': event['options'],
                        'similarity': similarity
                    })
    
    # 按相似度排序，取最匹配的前3个
    found_events.sort(key=lambda x: x['similarity'], reverse=True)
    return found_events[:3] if found_events else None

def format_options(options) -> str:
    """格式化选项信息"""
    result = []
    for i, opt in enumerate(options):
        if 'option' in opt and 'gain_list' in opt:
            option_text = opt['option']
            gains = opt['gain_list']
            
            result.append(f"选项{i+1}「{option_text}」:")
            for gain in gains:
                result.append(f"  {gain}")
    
    return '\n'.join(result)

def format_event_info(event) -> str:
    """格式化事件信息"""
    event_type = EVENT_TYPE_NAMES.get(event['event_type'], '未知剧情')
    
    msg = [
        f"协助卡「{event['card_name']}」",
        f"事件类型：{event_type}",
        f"事件名称：{event['story_name']}",
        "选项效果："
    ]
    
    options_text = format_options(event['options'])
    msg.append(options_text)
    
    return '\n'.join(msg)

# 定时任务
@sv.scheduled_job('cron', hour=4, minute=30)
async def daily_update():
    """每天凌晨4:30自动更新数据"""
    sv.logger.info("开始执行每日数据更新...")
    success = await update_data()
    if success:
        sv.logger.info("每日数据更新完成")
    else:
        sv.logger.error("每日数据更新失败")

# 命令处理函数
@sv.on_prefix(('uma事件', '马娘事件', '赛马娘事件'))
async def query_uma_event(bot, ev: CQEvent):
    # 提取查询关键词
    keyword = filt_message(ev.message.extract_plain_text().strip())
    if not keyword:
        await bot.send(ev, '请输入要查询的协助卡事件关键词~')
        return
        
    # 如果数据为空，尝试加载本地数据
    global support_cards, cards_events
    if not support_cards or not cards_events:
        support_cards, cards_events = load_data()
        
    # 如果还是为空，说明需要初始化数据
    if not support_cards or not cards_events:
        await bot.send(ev, '正在初始化协助卡数据，请稍等片刻喵~')
        success = await update_data()
        if not success:
            await bot.send(ev, '初始化协助卡数据失败，请联系管理员呜呜呜>_<')
            return
        await bot.send(ev, '协助卡数据初始化完成啦~！')
    
    # 查找事件
    events = find_events_by_name(keyword)
    if not events:
        await bot.send(ev, f'找不到与「{keyword}」相关的协助卡事件呢，请换个关键词试试吧~')
        return
    
    # 发送查询结果
    for event in events:
        msg = format_event_info(event)
        await bot.send(ev, msg)

@sv.on_fullmatch(('更新uma数据', '更新赛马娘数据'))
async def update_uma_data(bot, ev: CQEvent):
    # 只允许管理员更新数据
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有管理员才能执行这个操作哦~')
        return
        
    await bot.send(ev, '开始更新赛马娘协助卡数据，这可能需要一些时间，请耐心等待喵~')
    success = await update_data()
    if success:
        await bot.send(ev, '赛马娘协助卡数据更新完成啦~！')
    else:
        await bot.send(ev, '赛马娘协助卡数据更新失败了呜呜呜>_<')

@sv.on_fullmatch(('测试uma接口', '测试赛马娘接口'))
async def test_uma_api(bot, ev: CQEvent):
    if not priv.check_priv(ev, priv.ADMIN):
        await bot.send(ev, '只有管理员才能执行这个操作哦~')
        return
    
    await bot.send(ev, '正在测试API接口，请稍等...')
    resp = await test_api_auth()
    
    if 'code' in resp and resp['code'] == 0:
        await bot.send(ev, f'API测试成功！请求ID: {resp.get("request_id", "未知")}')
    else:
        await bot.send(ev, f'API测试失败: {resp}')

# 初始化时尝试加载数据
support_cards, cards_events = load_data()

def generate_sign_params() -> Dict[str, str]:
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