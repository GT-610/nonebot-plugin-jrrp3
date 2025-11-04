'''Description: 
version: 3.0
Author: Rene8028
Date: 2022-07-20 21:58:25
LastEditors: GT-610
LastEditTime: 2025-10-25 17:20:00
'''

import datetime
import sqlite3
from nonebot import require, get_driver

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")

# 获取驱动
driver = get_driver()

from nonebot.log import logger
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna import Alconna, on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage
from nonebot_plugin_localstore import get_plugin_data_dir
import random
from datetime import date

# 插件元数据
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="每日人品",
    description="更加现代化的 NoneBot2 每日人品插件，支持查询今日、本周、本月和历史平均人品，提供详细的运势评价，并支持数据持久化存储。",
    usage="jrrp/今日人品/今日运势 - 查询今日人品指数\nweekjrrp/本周人品/本周运势/周运势 - 查询本周平均人品\nmonthjrrp/本月人品/本月运势/月运势 - 查询本月平均人品\nalljrrp/总人品/平均人品/平均运势 - 查询历史平均人品",

    type="application",
    # 发布必填，当前有效类型有：`library`（为其他插件编写提供功能），`application`（向机器人用户提供功能）。

    homepage="https://github.com/GT-610/nonebot-plugin-jrrp3",
    # 发布必填。

    supported_adapters={"~onebot.v11"},
    # 支持的适配器集合，其中 `~` 在此处代表前缀 `nonebot.adapters.`，其余适配器亦按此格式填写。
    # 若插件可以保证兼容所有适配器（即仅使用基本适配器功能）可不填写，否则应该列出插件支持的适配器。
)


# 使用nonebot_plugin_localstore获取标准数据存储路径
plugin_data_dir = get_plugin_data_dir()
# 在标准数据目录下创建jrrp3子目录并设置数据库文件路径
DB_PATH = plugin_data_dir / "jrrpdata.db"

# 确保数据目录存在
data_dir = DB_PATH.parent
data_dir.mkdir(parents=True, exist_ok=True)

logger.debug(f"数据库路径: {DB_PATH}")

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

# 在驱动启动时初始化数据库
@driver.on_startup
async def startup():
    init_database()

#自定义数值对应回复
def luck_simple(num):
    if num == 100:
        return '超吉','100！100诶！！你就是欧皇？'
    elif num == 0:
        return '超凶(大寄)','？？？反向欧皇？'
    elif num > 75:
        return '大吉','好耶！今天运气真不错呢'
    elif num > 65:
        return '吉','哦豁，今天运气还顺利哦'
    elif num > 62:
        return '半吉','emm，今天运气一般般呢'
    elif num > 58:
        return '小吉','还……还行吧，今天运气稍差一点点呢'
    elif num > 53:
        return '末小吉','唔……今天运气有点差哦'
    elif num > 18:
        return '末吉','呜哇，今天运气应该不太好'
    elif num > 9:
        return '凶','啊这……(没错……是百分制)，今天还是吃点好的吧'
    else:
        return '大凶','啊这……(个位数可还行)，今天还是吃点好的吧'
    
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
