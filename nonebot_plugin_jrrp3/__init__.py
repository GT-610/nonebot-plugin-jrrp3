'''Description: 
version: 3.0
Author: Rene8028
Date: 2022-07-20 21:58:25
LastEditors: GT-610
LastEditTime: 2025-11-11 17:05:19
'''

import datetime
import sqlite3
import json
import yaml
import os
from nonebot import require, get_driver

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")

# 获取驱动
driver = get_driver()

from nonebot.log import logger
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna import Alconna, on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage
from nonebot_plugin_localstore import get_plugin_data_dir, get_plugin_config_dir
import random
from datetime import date

# 使用nonebot-plugin-localstore获取标准配置存储路径
plugin_config_dir = get_plugin_config_dir()
# 使用nonebot-plugin-localstore获取标准数据存储路径
plugin_data_dir = get_plugin_data_dir()

# 配置文件路径
CONFIG_FILE_YAML = plugin_config_dir / "jrrp_config.yaml"
CONFIG_FILE_JSON = plugin_config_dir / "jrrp_config.json"
# 确保配置目录存在
plugin_config_dir.mkdir(parents=True, exist_ok=True)

# 默认配置
DEFAULT_CONFIG = {
    "special_values": {
        "100": {
            "level": "超吉",
            "description": "100！100诶！！你就是欧皇？"
        },
        "0": {
            "level": "超凶(大寄)",
            "description": "？？？反向欧皇？"
        }
    },
    "ranges": [
        {
            "min": 76,
            "max": 99,
            "level": "大吉",
            "description": "好耶！今天运气真不错呢"
        },
        {
            "min": 66,
            "max": 75,
            "level": "吉",
            "description": "哦豁，今天运气还顺利哦"
        },
        {
            "min": 63,
            "max": 65,
            "level": "半吉",
            "description": "emm，今天运气一般般呢"
        },
        {
            "min": 59,
            "max": 62,
            "level": "小吉",
            "description": "还……还行吧，今天运气稍差一点点呢"
        },
        {
            "min": 54,
            "max": 58,
            "level": "末小吉",
            "description": "唔……今天运气有点差哦"
        },
        {
            "min": 19,
            "max": 53,
            "level": "末吉",
            "description": "呜哇，今天运气应该不太好"
        },
        {
            "min": 10,
            "max": 18,
            "level": "凶",
            "description": "啊这……(没错……是百分制)，今天还是吃点好的吧"
        },
        {
            "min": 1,
            "max": 9,
            "level": "大凶",
            "description": "啊这……(个位数可还行)，今天还是吃点好的吧"
        }
    ]
}

# 全局配置变量
plugin_config = None

# 插件元数据
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

__plugin_meta__ = PluginMetadata(
    name="每日人品",
    description="更加现代化的 NoneBot2 每日人品插件，支持查询今日、本周、本月和历史平均人品，提供详细的运势评价，并支持数据持久化存储。",
    usage="jrrp/今日人品/今日运势 - 查询今日人品指数\nweekjrrp/本周人品/本周运势/周运势 - 查询本周平均人品\nmonthjrrp/本月人品/本月运势/月运势 - 查询本月平均人品\nalljrrp/总人品/平均人品/平均运势 - 查询历史平均人品",

    type="application",
    # 发布必填，当前有效类型有：`library`（为其他插件编写提供功能），`application`（向机器人用户提供功能）。

    homepage="https://github.com/GT-610/nonebot-plugin-jrrp3",
    # 发布必填。

    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    # 使用 inherit_supported_adapters 从 alconna 插件继承支持的适配器
)


# 在标准数据目录下创建jrrp3子目录并设置数据库文件路径
DB_PATH = plugin_data_dir / "jrrpdata.db"

# 确保数据目录存在
data_dir = DB_PATH.parent
data_dir.mkdir(parents=True, exist_ok=True)

logger.debug(f"数据库路径: {DB_PATH}")
logger.debug(f"配置文件路径(YAML): {CONFIG_FILE_YAML}")
logger.debug(f"配置文件路径(JSON): {CONFIG_FILE_JSON}")

# 加载配置文件
def load_config():
    """加载配置文件，如果不存在则创建默认配置"""
    global plugin_config
    
    # 检查两种配置文件是否同时存在
    if CONFIG_FILE_YAML.exists() and CONFIG_FILE_JSON.exists():
        # 当两种格式的配置文件同时存在时，提示冲突
        logger.warning(
            f"配置文件冲突警告: YAML 文件({CONFIG_FILE_YAML})和 JSON 文件({CONFIG_FILE_JSON})同时存在!\n"
            f"系统将优先加载 YAML 格式配置文件。\n"
            f"建议删除其中一个文件以避免混淆。"
        )
        # 默认加载YAML格式
        try:
            with open(CONFIG_FILE_YAML, 'r', encoding='utf-8') as f:
                plugin_config = yaml.safe_load(f)
            logger.info(f"优先加载YAML配置文件: {CONFIG_FILE_YAML}")
            return
        except Exception as e:
            logger.error(f"加载YAML配置文件失败: {e}")
            # 如果YAML加载失败，尝试JSON
            try:
                with open(CONFIG_FILE_JSON, 'r', encoding='utf-8') as f:
                    plugin_config = json.load(f)
                logger.warning(f"YAML加载失败，尝试加载JSON配置文件: {CONFIG_FILE_JSON}")
                return
            except Exception as e:
                logger.error(f"加载JSON配置文件失败: {e}")
    
    # 如果只有一种格式存在，加载对应格式
    elif CONFIG_FILE_YAML.exists():
        try:
            with open(CONFIG_FILE_YAML, 'r', encoding='utf-8') as f:
                plugin_config = yaml.safe_load(f)
            logger.info(f"成功加载YAML配置文件: {CONFIG_FILE_YAML}")
            return
        except Exception as e:
            logger.error(f"加载YAML配置文件失败: {e}")
    
    elif CONFIG_FILE_JSON.exists():
        try:
            with open(CONFIG_FILE_JSON, 'r', encoding='utf-8') as f:
                plugin_config = json.load(f)
            logger.info(f"成功加载JSON配置文件: {CONFIG_FILE_JSON}")
            return
        except Exception as e:
            logger.error(f"加载JSON配置文件失败: {e}")
    
    # 如果都不存在，创建默认YAML配置文件
    try:
        with open(CONFIG_FILE_YAML, 'w', encoding='utf-8') as f:
            yaml.dump(DEFAULT_CONFIG, f, allow_unicode=True, default_flow_style=False)
        plugin_config = DEFAULT_CONFIG
        logger.info(f"创建默认YAML配置文件: {CONFIG_FILE_YAML}")
    except Exception as e:
        logger.error(f"创建默认配置文件失败: {e}")
        # 如果创建配置文件失败，使用内存中的默认配置
        plugin_config = DEFAULT_CONFIG
        logger.warning("使用内存中的默认配置")

# 数据库连接辅助函数
def get_db_connection():
    """获取数据库连接"""
    return sqlite3.connect(str(DB_PATH))

# 初始化数据库
def init_database():
    """初始化数据库表"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            create_tb_cmd = '''
            CREATE TABLE IF NOT EXISTS jdata
            (QQID int,
            Value int,
            Date text);
            '''
            cursor.execute(create_tb_cmd)
            conn.commit()
        logger.info("数据库表初始化成功")
    except Exception as e:
        logger.error(f"数据库表初始化失败: {e}")

# 在驱动启动时初始化数据库和加载配置
@driver.on_startup
async def startup():
    load_config()
    init_database()

#自定义数值对应回复
def luck_simple(num):
    global plugin_config
    
    # 确保配置已加载
    if plugin_config is None:
        load_config()
    
    # 检查特殊值
    special_values = plugin_config.get("special_values", {})
    if str(num) in special_values:
        special_config = special_values[str(num)]
        return special_config["level"], special_config["description"]
    
    # 检查范围值
    ranges = plugin_config.get("ranges", [])
    for range_config in ranges:
        if range_config["min"] <= num <= range_config["max"]:
            return range_config["level"], range_config["description"]
    
    # 如果没有匹配到，返回默认值
    return "未知", "无法确定运势级别"
    
# 新增数据
def insert_tb(qqid, value, date):
    """向数据库插入新的人品记录"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 使用参数化查询避免SQL注入
            insert_tb_cmd = 'INSERT INTO jdata(QQID, Value, Date) VALUES(?, ?, ?)'
            cursor.execute(insert_tb_cmd, (qqid, value, date))
            conn.commit()
    except Exception as e:
        logger.error(f"插入数据失败: {e}")
        raise

# 查询历史数据
def select_tb_all(qqid):
    """查询用户的所有历史人品记录"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            select_tb_cmd = 'SELECT * FROM jdata WHERE QQID = ?'
            cursor.execute(select_tb_cmd, (qqid,))
            return cursor.fetchall()
    except Exception as e:
        logger.error(f"查询历史数据失败: {e}")
        return []

# 查询今日是否存在数据
def select_tb_today(qqid, date):
    """查询用户今日是否已经查询过人品"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            select_tb_cmd = 'SELECT * FROM jdata WHERE QQID = ? AND Date = ?'
            cursor.execute(select_tb_cmd, (qqid, date))
            results = cursor.fetchall()
            return bool(results)
    except Exception as e:
        logger.error(f"查询今日数据失败: {e}")
        return False
#判断是否本周
def same_week(dateString):
    d1 = datetime.datetime.strptime(dateString,'%y%m%d')
    d2 = datetime.datetime.today()
    return d1.isocalendar()[1] == d2.isocalendar()[1] \
              and d1.year == d2.year
#判断是否本月
def same_month(dateString):
    d1 = datetime.datetime.strptime(dateString,'%y%m%d')
    d2 = datetime.datetime.today()
    return d1.month == d2.month \
              and d1.year == d2.year

# 使用 Alconna 创建命令
jrrp_cmd = Alconna("jrrp")
alljrrp_cmd = Alconna("alljrrp")
monthjrrp_cmd = Alconna("monthjrrp")
weekjrrp_cmd = Alconna("weekjrrp")

# 创建命令处理器，保留所有现有的命令格式和别名
jrrp = on_alconna(
    jrrp_cmd,
    aliases={"今日人品", "今日运势"},
    use_cmd_start=True,
    block=True
)

alljrrp = on_alconna(
    alljrrp_cmd,
    aliases={'总人品', '平均人品', '平均运势'},
    use_cmd_start=True,
    block=True
)

monthjrrp = on_alconna(
    monthjrrp_cmd,
    aliases={'本月人品', '本月运势', '月运势'},
    use_cmd_start=True,
    block=True
)

weekjrrp = on_alconna(
    weekjrrp_cmd,
    aliases={'本周人品', '本周运势', '周运势'},
    use_cmd_start=True,
    block=True
)

@jrrp.handle()
async def jrrp_handle(bot: Bot, event: Event):
    """处理今日人品查询命令"""
    try:
        user_id = event.get_user_id()
        today_date = date.today().strftime("%y%m%d")
        
        # 生成随机数
        rnd = random.Random()
        rnd.seed(int(today_date) + int(user_id))
        lucknum = rnd.randint(1, 100)
        
        # 如果今日未查询过，则保存记录
        if not select_tb_today(user_id, today_date):
            insert_tb(user_id, lucknum, today_date)
        
        # 获取运势评价
        luck_level, luck_desc = luck_simple(lucknum)
        
        # 发送结果
        await UniMessage.text(
            f' 您今日的幸运指数是 {lucknum}，为“{luck_level}”，{luck_desc}'
        ).send(at_sender=True)
        await jrrp.finish()
        return  # 确保finish()后不会继续执行
    except Exception as e:
        # 避免捕获FinishedException
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise  # 重新抛出FinishedException
        logger.error(f"处理今日人品查询出错: {e}")
        await UniMessage.text(" 处理请求时出错，请稍后重试").send(at_sender=True)
        await jrrp.finish()

@alljrrp.handle()
async def alljrrp_handle(bot: Bot, event: Event):
    """处理历史平均人品查询命令"""
    try:
        user_id = event.get_user_id()
        alldata = select_tb_all(user_id)
        
        if not alldata:
            await UniMessage.text(f' 您还没有过历史人品记录！').send(at_sender=True)
            await alljrrp.finish()
        
        # 计算平均值
        times = len(alldata)
        allnum = sum(int(item[1]) for item in alldata)
        avg_luck = round(allnum / times, 1)
        
        await UniMessage.text(
            f' 您一共使用了 {times} 天 jrrp，您历史平均的幸运指数是 {avg_luck}'
        ).send(at_sender=True)
        await alljrrp.finish()
    except Exception as e:
        # 避免捕获FinishedException
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise  # 重新抛出FinishedException
        logger.error(f"处理历史平均人品查询出错: {e}")
        await UniMessage.text(" 处理请求时出错，请稍后重试").send(at_sender=True)
        await alljrrp.finish()

@monthjrrp.handle()
async def monthjrrp_handle(bot: Bot, event: Event):
    """处理本月平均人品查询命令"""
    try:
        user_id = event.get_user_id()
        alldata = select_tb_all(user_id)
        
        # 筛选本月数据
        month_data = [item for item in alldata if same_month(item[2])]
        
        if not month_data:
            await UniMessage.text(f' 您本月还没有过人品记录！').send(at_sender=True)
            await monthjrrp.finish()
        
        # 计算平均值
        times = len(month_data)
        allnum = sum(int(item[1]) for item in month_data)
        avg_luck = round(allnum / times, 1)
        
        await UniMessage.text(
            f' 您本月共使用了 {times} 天 jrrp，平均的幸运指数是 {avg_luck}'
        ).send(at_sender=True)
        await monthjrrp.finish()
    except Exception as e:
        # 避免捕获FinishedException
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise  # 重新抛出FinishedException
        logger.error(f"处理本月平均人品查询出错: {e}")
        await UniMessage.text(" 处理请求时出错，请稍后重试").send(at_sender=True)
        await monthjrrp.finish()

@weekjrrp.handle()
async def weekjrrp_handle(bot: Bot, event: Event):
    """处理本周平均人品查询命令"""
    try:
        user_id = event.get_user_id()
        alldata = select_tb_all(user_id)
        
        if not alldata:
            await UniMessage.text(f' 您还没有过历史人品记录！').send(at_sender=True)
            await weekjrrp.finish()
        
        # 筛选本周数据
        week_data = [item for item in alldata if same_week(item[2])]
        
        if not week_data:
            await UniMessage.text(f' 您本周还没有过人品记录！').send(at_sender=True)
            await weekjrrp.finish()
        
        # 计算平均值
        times = len(week_data)
        allnum = sum(int(item[1]) for item in week_data)
        avg_luck = round(allnum / times, 1)
        
        await UniMessage.text(
            f' 您本周共使用了 {times} 天 jrrp，平均的幸运指数是 {avg_luck}'
        ).send(at_sender=True)
        await weekjrrp.finish()
    except Exception as e:
        # 避免捕获FinishedException
        from nonebot.exception import FinishedException
        if isinstance(e, FinishedException):
            raise  # 重新抛出FinishedException
        logger.error(f"处理本周平均人品查询出错: {e}")
        await UniMessage.text(" 处理请求时出错，请稍后重试").send(at_sender=True)
        await weekjrrp.finish()
