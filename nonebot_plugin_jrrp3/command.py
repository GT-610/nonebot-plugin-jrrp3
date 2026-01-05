from dataclasses import dataclass
from typing import Callable, Optional
from datetime import date

from nonebot.log import logger
from nonebot.adapters import Event
from nonebot_plugin_alconna import Alconna, on_alconna, Args
from nonebot_plugin_alconna.uniseg import UniMessage
from nonebot.exception import FinishedException

from .database import insert_tb, select_tb_all, select_tb_today, same_week, same_month
from .utils import calculate_luck_level, generate_luck_value, calculate_average_luck, filter_data_by_date
from .config import get_config

@dataclass
class Command:
    keywords: tuple[str, ...]
    args: Optional[Args] = None
    func: Optional[Callable] = None

def create_command_handler(command_name: str, handler_func: Callable[[Event], str]):
    async def handle(event: Event) -> str:
        try:
            return handler_func(event)
        except Exception as e:
            logger.error(f"处理 {command_name} 命令时出错: {e}")
            raise
    return handle

async def send_result(result: str, at_sender: bool = True) -> None:
    await UniMessage.text(result).send(at_sender=at_sender)

def jrrp_handle_func(event: Event) -> str:
    user_id = event.get_user_id()
    today_date = date.today().strftime("%y%m%d")
    
    seed = int(today_date) + int(user_id)
    
    config = get_config()
    min_luck = config.get("min_luck", 0)
    max_luck = config.get("max_luck", 100)
    
    lucknum = generate_luck_value(min_luck, max_luck, seed)
    
    if not select_tb_today(user_id, today_date):
        insert_tb(user_id, lucknum, today_date)
    
    luck_level, luck_desc = calculate_luck_level(lucknum, config.get("ranges", []))
    
    return f' 您今日的幸运指数是 {lucknum}，为"{luck_level}"，{luck_desc}'

def alljrrp_handle_func(event: Event) -> str:
    user_id = event.get_user_id()
    alldata = select_tb_all(user_id)
    
    if not alldata:
        return f' 您还没有过历史人品记录！'
    
    times, avg_luck = calculate_average_luck(alldata)
    
    return f' 您一共使用了 {times} 天 jrrp，您历史平均的幸运指数是 {avg_luck}'

def monthjrrp_handle_func(event: Event) -> str:
    user_id = event.get_user_id()
    alldata = select_tb_all(user_id)
    
    month_data = filter_data_by_date(alldata, same_month)
    
    if not month_data:
        return f' 您本月还没有过人品记录！'
    
    times, avg_luck = calculate_average_luck(month_data)
    
    return f' 您本月共使用了 {times} 天 jrrp，平均的幸运指数是 {avg_luck}'

def weekjrrp_handle_func(event: Event) -> str:
    user_id = event.get_user_id()
    alldata = select_tb_all(user_id)
    
    if not alldata:
        return f' 您还没有过历史人品记录！'
    
    week_data = filter_data_by_date(alldata, same_week)
    
    if not week_data:
        return f' 您本周还没有过人品记录！'
    
    times, avg_luck = calculate_average_luck(week_data)
    
    return f' 您本周共使用了 {times} 天 jrrp，平均的幸运指数是 {avg_luck}'

def jrrphelp_handle_func(event: Event) -> str:
    return '''人品插件使用说明（记得加前缀）：

支持的命令：
- jrrp / 今日人品 / 今日运势：查询今日人品指数
- weekjrrp / 本周人品 / 本周运势 / 周运势：查询本周平均人品
- monthjrrp / 本月人品 / 本月运势 / 月运势：查询本月平均人品
- alljrrp / 总人品 / 平均人品 / 平均运势：查询历史平均人品

插件源代码：https://github.com/GT-610/nonebot-plugin-jrrp3'''

jrrp_cmd = Alconna("jrrp")
alljrrp_cmd = Alconna("alljrrp")
monthjrrp_cmd = Alconna("monthjrrp")
weekjrrp_cmd = Alconna("weekjrrp")
jrrphelp_cmd = Alconna("jrrphelp")

commands = [
    Command(("jrrp", "今日人品", "今日运势"), func=jrrp_handle_func),
    Command(("alljrrp", "总人品", "平均人品", "平均运势"), func=alljrrp_handle_func),
    Command(("monthjrrp", "本月人品", "本月运势", "月运势"), func=monthjrrp_handle_func),
    Command(("weekjrrp", "本周人品", "本周运势", "周运势"), func=weekjrrp_handle_func),
    Command(("jrrphelp", "jrrp帮助", "人品帮助", "运势帮助"), func=jrrphelp_handle_func),
]

async def register_commands():
    handlers = [
        ("jrrp", jrrp_cmd, {"今日人品", "今日运势"}, jrrp_handle_func),
        ("alljrrp", alljrrp_cmd, {"总人品", "平均人品", "平均运势"}, alljrrp_handle_func),
        ("monthjrrp", monthjrrp_cmd, {"本月人品", "本月运势", "月运势"}, monthjrrp_handle_func),
        ("weekjrrp", weekjrrp_cmd, {"本周人品", "本周运势", "周运势"}, weekjrrp_handle_func),
        ("jrrphelp", jrrphelp_cmd, {"jrrp帮助", "人品帮助", "运势帮助"}, jrrphelp_handle_func),
    ]
    
    for name, cmd, aliases, func in handlers:
        matcher = on_alconna(cmd, aliases=aliases, use_cmd_start=True, block=True)
        
        @matcher.handle()
        async def handler(event: Event, func=func, name=name):
            try:
                result = func(event)
                await send_result(result)
            except FinishedException:
                raise
            except Exception as e:
                logger.error(f"处理 {name} 命令时出错: {e}")
                await send_result(" 处理请求时出错，请稍后重试")
