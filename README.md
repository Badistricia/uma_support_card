# 赛马娘协助卡查询插件

一个简单的赛马娘协助卡事件查询插件，用于在HoshinoBot中使用。

## 功能

- 模糊搜索赛马娘协助卡事件
- 显示事件的详细信息和选项效果
- 数据实时更新
- 每日自动更新数据
- API鉴权自诊断

## 安装方法

1. 将本插件放置在 HoshinoBot 的 `modules` 目录下
2. 在 `config.py` 中设置您的 bilibili API 密钥（见下方配置说明）
3. 在 `__bot__.py` 的 `MODULES_ON` 中添加 `'uma_support_card'`
4. 重启 Bot

## 配置说明

在开始使用前，请编辑 `config.py` 文件，设置您的 bilibili API 密钥：

```python
# API 配置
class ApiConfig:
    # bilibili API 密钥 (请替换为您的有效值)
    APPKEY = "你的appkey"  # 必须修改为有效值
    APPSEC = "你的appsec"  # 必须修改为有效值
```

您可以通过以下方式获取 bilibili API 密钥：
1. 前往 [Bilibili开放平台](https://www.bilibili.com/account/api) 申请
2. 或使用已有的第三方应用密钥

> 注意：由于 bilibili API 政策变更，现在请求接口必须提供有效的 appkey，ts，nonce和sign等参数

## 使用方法

### 查询协助卡事件

使用以下命令进行查询：

```
uma事件 事件关键词
```

例如：
- `uma事件 云霄飞车`
- `uma事件 蹄铁`
- `马娘事件 这也烦恼`
- `赛马娘事件 胜利舞台`

### 更新数据

管理员可以使用以下命令手动更新数据：

```
更新uma数据
```

或

```
更新赛马娘数据
```

### 测试API接口

管理员可以使用以下命令测试API接口是否正常工作：

```
测试uma接口
```

或

```
测试赛马娘接口
```

## 数据存储

数据存储在 `data/` 目录下：
- `cards_data.json`: 存储协助卡基础信息
- `events_data.json`: 存储事件详细数据

## 自动更新机制

插件会在每天凌晨4:30自动更新数据，确保数据始终保持最新。
首次使用时，插件也会自动初始化和下载所需数据。

## 数据来源

数据来源于Bilibili赛马娘工具站：
- 协助卡列表: https://api.game.bilibili.com/game/player/tools/uma/support_cards
- 协助卡详情: https://api.game.bilibili.com/game/player/tools/uma/support_card_detail

## 注意事项

- 首次使用时需要从API获取数据，可能需要一些时间
- 查询使用模糊匹配，返回最相关的前3个结果
- 请确保您的 appkey 和 appsec 有效，否则将无法获取数据
- 如遇到API请求失败，可以使用`测试uma接口`命令进行诊断 