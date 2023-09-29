'''
Descripttion: 
version: 2.0
Author: Rene8028
Date: 2022-07-20 21:58:25
LastEditors: UKMeng
LastEditTime: 2023-09-26 15:15:46
'''


import datetime
from pathlib import Path
import sqlite3
from nonebot import on_fullmatch, require, on_command

require("nonebot_plugin_saa")

from nonebot.log import logger
#from nonebot.adapters.onebot.v11.bot import Bot, Event
#from nonebot.adapters.onebot.v11.message import Message
# from nonebot.adapters.red.bot import Bot, Event
# from nonebot.adapters.red.message import MessageSegment
from nonebot.adapters import Bot, Event
from nonebot_plugin_saa import Text, extract_target, MessageFactory
import random
from datetime import date

data_dir = Path("data/jrrp2").absolute()
data_dir.mkdir(parents=True, exist_ok=True)

# '''数据库初始化'''
jdb = sqlite3.connect("data/jrrp2/jrrpdata.db")
cursor = jdb.cursor()

# '''表初始化'''
try:
    create_tb_cmd='''
    CREATE TABLE IF NOT EXISTS jdata
    (QQID int,
    Value int,
    Date text);
    '''
    cursor.execute(create_tb_cmd)
except:
    logger.error("jrrp2 Create data table failed")

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
    
#新增数据
def insert_tb(qqid,value,date):
    insert_tb_cmd = f'insert into jdata(QQID, Value, Date) values("{qqid}","{value}","{date}")'
    cursor.execute(insert_tb_cmd)
    jdb.commit()
#查询历史数据
def select_tb_all(qqid):
    select_tb_cmd = f'select *from jdata where QQID = {qqid}'
    cursor.execute(select_tb_cmd)
    return cursor.fetchall()
#查询今日是否存在数据
def select_tb_today(qqid,date):
    select_tb_cmd = f'select *from jdata where QQID = {qqid} and Date = {date}'
    cursor.execute(select_tb_cmd)
    results = cursor.fetchall()
    if results:
        return True
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

jrrp = on_fullmatch(("jrrp", "j", "今日人品", "今日运势"))
@jrrp.handle()
async def jrrp_handle(bot: Bot, event: Event):
    #target = extract_target(event)
    #logger.debug(int(event.get_user_id()))
    rnd = random.Random()
    rnd.seed(int(date.today().strftime("%y%m%d")) + int(event.get_user_id()))
    lucknum = rnd.randint(1,100)
    if not select_tb_today(event.get_user_id(),date.today().strftime("%y%m%d")):
        insert_tb(event.get_user_id(),lucknum,date.today().strftime("%y%m%d"))
    
    #await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您今日的幸运指数是{lucknum}，为"{luck_simple(lucknum)[0]}"，{luck_simple(lucknum)[1]}'))
    await MessageFactory(f' 您今日的幸运指数是{lucknum}，为"{luck_simple(lucknum)[0]}"，{luck_simple(lucknum)[1]}').send(reply=False, at_sender=True)
    #m = MessageSegment.text(f' 您今日的幸运指数是{lucknum}，为"{luck_simple(lucknum)[0]}"，{luck_simple(lucknum)[1]}')
    #m2 = MessageSegment.reply(event.msgSeq, event.msgId, event.get_user_id())
    #await bot.send(event, [m2, m])
    await jrrp.finish()

alljrrp = on_command("alljrrp",None,aliases={'总人品','平均人品','平均运势'})
@alljrrp.handle()
async def alljrrp_handle(bot: Bot, event: Event):
    alldata = select_tb_all(event.get_user_id())
    if alldata == None:
        # await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您还没有过历史人品记录！'))
        await MessageFactory(f' 您还没有过历史人品记录！').send(at_sender=True)
        await jrrp.finish()
    times = len(alldata)
    allnum = 0
    for i in alldata:
        allnum = allnum + int(i[1])
    # await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您一共使用了{times}天jrrp，您历史平均的幸运指数是{round(allnum / times,1)}'))
    await MessageFactory(f' 您一共使用了{times}天jrrp，您历史平均的幸运指数是{round(allnum / times,1)}').send(at_sender=True)
    await jrrp.finish()

monthjrrp = on_command("monthjrrp",None,aliases={'本月人品','本月运势','月运势'})
@monthjrrp.handle()
async def monthjrrp_handle(bot: Bot, event: Event):
    alldata = select_tb_all(event.get_user_id())
    times = 0
    allnum = 0
    for i in alldata:
        if same_month(i[2]):
            times = times + 1
            allnum = allnum + int(i[1])
    if times == 0:
        await MessageFactory(f' 您本月还没有过人品记录！').send(at_sender=True)
        #await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您本月还没有过人品记录！'))
        jrrp.finish()
    # await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您本月共使用了{times}天jrrp，平均的幸运指数是{round(allnum / times,1)}'))
    await MessageFactory(f' 您本月共使用了{times}天jrrp，平均的幸运指数是{round(allnum / times,1)}').send(at_sender=True)
    await jrrp.finish()


weekjrrp = on_command("weekjrrp",None,aliases={'本周人品','本周运势','周运势'})
@weekjrrp.handle()
async def weekjrrp_handle(bot: Bot, event: Event):
    alldata = select_tb_all(event.get_user_id())
    if alldata == None:
        # await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您还没有过历史人品记录！'))
        await MessageFactory(f' 您还没有过历史人品记录！').send(at_sender=True)
        await jrrp.finish()
    times = 0
    allnum = 0
    for i in alldata:
        if same_week(i[2]):
            times = times + 1
            allnum = allnum + int(i[1])
    if times == 0:
        # await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您本周还没有过人品记录！'))
        await MessageFactory(f' 您本周还没有过人品记录！').send(at_sender=True)
        await jrrp.finish()
    #await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您本周共使用了{times}次jrrp，平均的幸运指数是{round(allnum / times,1)}'))
    await MessageFactory(f' 您本周共使用了{times}次jrrp，平均的幸运指数是{round(allnum / times,1)}').send(at_sender=True)
    await jrrp.finish()
