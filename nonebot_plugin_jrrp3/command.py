from dataclasses import dataclass
from typing import Callable, Optional, Dict, Any
from datetime import date

from nonebot.log import logger
from nonebot.adapters import Event
from nonebot_plugin_alconna import Alconna, on_alconna, Args
from nonebot_plugin_alconna.uniseg import UniMessage
from nonebot.exception import FinishedException

# 导入需要的模块和函数
from .database import insert_tb, select_tb_all, select_tb_today, same_week, same_month
from .utils import calculate_luck_level, generate_luck_value, calculate_average_luck, filter_week_data, filter_month_data

# 定义命令数据类，用于存储命令关键词、参数和处理函数的映射关系
@dataclass
class Command:
    """命令数据类，封装命令关键词、参数和对应的处理函数"""
    keywords: tuple[str, ...]  # 命令关键词列表，用于触发命令
    args: Optional[Args] = None  # 参数定义，指定命令需要的参数类型（可选）
    func: Optional[Callable] = None  # 处理函数，执行对应操作

# 定义全局配置变量引用
plugin_config: Dict[str, Any] = None

# 设置全局配置的函数
def set_plugin_config(config: Dict[str, Any]):
    """设置插件配置，供外部模块调用"""
    global plugin_config
    plugin_config = config

# 命令处理函数
def jrrp_handle_func(event: Event) -> str:
    """处理今日人品查询的核心逻辑
    
    Args:
        event: 事件对象
    
    Returns:
        处理结果文本
    """
    try:
        user_id = event.get_user_id()
        today_date = date.today().strftime("%y%m%d")
        
        # 生成随机数种子
        seed = int(today_date) + int(user_id)
        
        # 获取已通过边界控制的随机数范围
        min_luck = plugin_config.get("min_luck", 0)
        max_luck = plugin_config.get("max_luck", 100)
        
        # 生成人品值
        lucknum = generate_luck_value(min_luck, max_luck, seed)
        
        # 如果今日未查询过，则保存记录
        if not select_tb_today(user_id, today_date):
            insert_tb(user_id, lucknum, today_date)
        
        # 获取运势评价
        luck_level, luck_desc = calculate_luck_level(lucknum, plugin_config.get("ranges", []))
        
        return f' 您今日的幸运指数是 {lucknum}，为"{luck_level}"，{luck_desc}'
    except Exception as e:
        logger.error(f"处理今日人品查询出错: {e}")
        raise

def alljrrp_handle_func(event: Event) -> str:
    """处理历史平均人品查询的核心逻辑
    
    Args:
        event: 事件对象
    
    Returns:
        处理结果文本
    """
    try:
        user_id = event.get_user_id()
        alldata = select_tb_all(user_id)
        
        if not alldata:
            return f' 您还没有过历史人品记录！'
        
        # 计算平均值
        times, avg_luck = calculate_average_luck(alldata)
        
        return f' 您一共使用了 {times} 天 jrrp，您历史平均的幸运指数是 {avg_luck}'
    except Exception as e:
        logger.error(f"处理历史平均人品查询出错: {e}")
        raise

def monthjrrp_handle_func(event: Event) -> str:
    """处理本月平均人品查询的核心逻辑
    
    Args:
        event: 事件对象
    
    Returns:
        处理结果文本
    """
    try:
        user_id = event.get_user_id()
        alldata = select_tb_all(user_id)
        
        # 筛选本月数据
        month_data = filter_month_data(alldata, same_month)
        
        if not month_data:
            return f' 您本月还没有过人品记录！'
        
        # 计算平均值
        times, avg_luck = calculate_average_luck(month_data)
        
        return f' 您本月共使用了 {times} 天 jrrp，平均的幸运指数是 {avg_luck}'
    except Exception as e:
        logger.error(f"处理本月平均人品查询出错: {e}")
        raise

def weekjrrp_handle_func(event: Event) -> str:
    """处理本周平均人品查询的核心逻辑
    
    Args:
        event: 事件对象
    
    Returns:
        处理结果文本
    """
    try:
        user_id = event.get_user_id()
        alldata = select_tb_all(user_id)
        
        if not alldata:
            return f' 您还没有过历史人品记录！'
        
        # 筛选本周数据
        week_data = filter_week_data(alldata, same_week)
        
        if not week_data:
            return f' 您本周还没有过人品记录！'
        
        # 计算平均值
        times, avg_luck = calculate_average_luck(week_data)
        
        return f' 您本周共使用了 {times} 天 jrrp，平均的幸运指数是 {avg_luck}'
    except Exception as e:
        logger.error(f"处理本周平均人品查询出错: {e}")
        raise

# 创建命令对象
jrrp_cmd = Alconna("jrrp")
alljrrp_cmd = Alconna("alljrrp")
monthjrrp_cmd = Alconna("monthjrrp")
weekjrrp_cmd = Alconna("weekjrrp")

# 创建命令列表
commands = [
    Command(("jrrp", "今日人品", "今日运势"), func=jrrp_handle_func),
    Command(("alljrrp", "总人品", "平均人品", "平均运势"), func=alljrrp_handle_func),
    Command(("monthjrrp", "本月人品", "本月运势", "月运势"), func=monthjrrp_handle_func),
    Command(("weekjrrp", "本周人品", "本周运势", "周运势"), func=weekjrrp_handle_func),
]

# 导出命令处理器注册函数
async def register_commands(plugin_config):
    """注册所有命令处理器"""
    # 设置全局配置变量
    set_plugin_config(plugin_config)
    
    # 今日人品命令处理器
    jrrp = on_alconna(
        jrrp_cmd,
        aliases={"今日人品", "今日运势"},
        use_cmd_start=True,
        block=True
    )
    
    @jrrp.handle()
    async def jrrp_handle(event: Event):
        # 使用装饰器处理异常
        result = jrrp_handle_func(event)
        await UniMessage.text(result).send(at_sender=True)
        await jrrp.finish()
    
    # 历史平均人品命令处理器
    alljrrp = on_alconna(
        alljrrp_cmd,
        aliases={"总人品", "平均人品", "平均运势"},
        use_cmd_start=True,
        block=True
    )
    
    @alljrrp.handle()
    async def alljrrp_handle(event: Event):
        result = alljrrp_handle_func(event)
        await UniMessage.text(result).send(at_sender=True)
        await alljrrp.finish()
    
    # 本月平均人品命令处理器
    monthjrrp = on_alconna(
        monthjrrp_cmd,
        aliases={"本月人品", "本月运势", "月运势"},
        use_cmd_start=True,
        block=True
    )
    
    @monthjrrp.handle()
    async def monthjrrp_handle(event: Event):
        result = monthjrrp_handle_func(event)
        await UniMessage.text(result).send(at_sender=True)
        await monthjrrp.finish()
    
    # 本周平均人品命令处理器
    weekjrrp = on_alconna(
        weekjrrp_cmd,
        aliases={"本周人品", "本周运势", "周运势"},
        use_cmd_start=True,
        block=True
    )
    
    @weekjrrp.handle()
    async def weekjrrp_handle(event: Event):
        result = weekjrrp_handle_func(event)
        await UniMessage.text(result).send(at_sender=True)
        await weekjrrp.finish()

# 错误处理装饰器
def handle_command_error(func):
    """装饰器函数，用于统一处理命令执行过程中的异常
    
    Args:
        func: 被装饰的命令处理函数
        
    Returns:
        装饰后的函数
    """
    async def wrapper(event: Event):
        try:
            result = func(event)
            await UniMessage.text(result).send(at_sender=True)
            await wrapper.finish()
        except Exception as e:
            if isinstance(e, FinishedException):
                raise
            await UniMessage.text(" 处理请求时出错，请稍后重试").send(at_sender=True)
            await wrapper.finish()
    return wrapper