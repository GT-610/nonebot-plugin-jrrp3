'''Descripttion: 
version: 3.0
Author: Rene8028
Date: 2022-07-20 21:58:25
LastEditors: GT-610
LastEditTime: 2025-10-25 17:20:00
'''

import datetime
from pathlib import Path
import sqlite3
from nonebot import require, get_driver

require("nonebot_plugin_alconna")

# 获取驱动
driver = get_driver()

from nonebot.log import logger
from nonebot.adapters import Bot, Event
from nonebot_plugin_alconna import Alconna, on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage
import random
from datetime import date

# 数据库路径
DB_PATH = Path("data/jrrp3/jrrpdata.db")

# 确保数据目录存在
data_dir = DB_PATH.parent
data_dir.mkdir(parents=True, exist_ok=True)

logger.info(f"数据库路径: {DB_PATH}")

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
            f' 您今日的幸运指数是{lucknum}，为"{luck_level}"，{luck_desc}'
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
            f' 您一共使用了 {times} 天jrrp，您历史平均的幸运指数是 {avg_luck}'
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
