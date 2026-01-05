import random
from typing import Callable
from nonebot.log import logger
from .constants import LuckValueBounds

def calculate_luck_level(num: int, ranges: list) -> tuple[str, str]:
    """根据人品数值计算运势级别和描述
    
    Args:
        num: 人品数值
        ranges: 运势级别范围配置列表
        
    Returns:
        tuple: (运势级别, 运势描述)
    """
    for range_config in ranges:
        min_val = range_config["min"]
        max_val = range_config["max"]
        if min_val <= num <= max_val:
            return range_config["level"], range_config["description"]
    
    return "未知", "你进入了虚空之地"

def generate_luck_value(min_luck: int, max_luck: int, seed: int) -> int:
    """根据用户ID和日期生成随机的人品数值
    
    Args:
        min_luck: 最小幸运值
        max_luck: 最大幸运值
        seed: 随机数种子（通常由日期和用户ID组成）
        
    Returns:
        int: 生成的人品数值
    """
    min_luck = max(LuckValueBounds.MIN_SAFE, min(int(min_luck), LuckValueBounds.MAX_SAFE))
    max_luck = max(LuckValueBounds.MIN_SAFE, min(int(max_luck), LuckValueBounds.MAX_SAFE))
    
    try:
        rnd = random.Random()
        rnd.seed(seed)
        return rnd.randint(min_luck, max_luck)
    except ValueError as e:
        logger.error(f"生成随机数时出错: {e}，使用默认范围")
        rnd = random.Random()
        rnd.seed(seed)
        return rnd.randint(LuckValueBounds.RANDINT_FALLBACK_MIN, LuckValueBounds.RANDINT_FALLBACK_MAX)

def calculate_average_luck(data: list) -> tuple[int, float]:
    """计算平均人品值
    
    Args:
        data: 人品记录列表，每个元素为(QQID, Value, Date)格式的元组
        
    Returns:
        tuple: (记录数量, 平均人品值)
    """
    if not data:
        return 0, 0
    
    times = len(data)
    allnum = sum(int(item[1]) for item in data)
    avg_luck = round(allnum / times, 1)
    
    return times, avg_luck

def filter_data_by_date(data: list, date_func: Callable[[str], bool]) -> list:
    """根据日期函数筛选数据
    
    Args:
        data: 全部人品记录列表，每个元素为(QQID, Value, Date)格式的元组
        date_func: 日期过滤函数，判断日期是否符合条件
        
    Returns:
        符合条件的数据列表
    """
    return [item for item in data if date_func(item[2])]