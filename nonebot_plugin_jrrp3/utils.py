import random
from nonebot.log import logger

# 安全边界定义
MIN_SAFE_VALUE = -999999999
MAX_SAFE_VALUE = 999999999

def calculate_luck_level(num: int, ranges: list) -> tuple:
    """根据人品数值计算运势级别和描述
    
    Args:
        num: 人品数值
        ranges: 运势级别范围配置列表
        
    Returns:
        tuple: (运势级别, 运势描述)
    """
    # 检查范围值（使用与randint一致的左闭右闭规则：[min, max]）
    for range_config in ranges:
        min_val = range_config["min"]
        max_val = range_config["max"]
        if min_val <= num <= max_val:
            return range_config["level"], range_config["description"]
    
    # 如果没有匹配到，返回默认值
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
    # 额外保险：再次确保在安全范围内
    min_luck = max(MIN_SAFE_VALUE, min(int(min_luck), MAX_SAFE_VALUE))
    max_luck = max(MIN_SAFE_VALUE, min(int(max_luck), MAX_SAFE_VALUE))
    
    # 安全生成随机数，避免极端值问题
    try:
        rnd = random.Random()
        rnd.seed(seed)
        lucknum = rnd.randint(min_luck, max_luck)
        return lucknum
    except ValueError as e:
        logger.error(f"生成随机数时出错: {e}，使用默认范围")
        rnd = random.Random()
        rnd.seed(seed)
        return rnd.randint(1, 100)

def calculate_average_luck(data: list) -> tuple:
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

def filter_week_data(data: list, date_func) -> list:
    """筛选本周的人品数据
    
    Args:
        data: 全部人品记录
        date_func: 日期过滤函数，判断是否为本周
        
    Returns:
        list: 本周的人品记录
    """
    return [item for item in data if date_func(item[2])]

def filter_month_data(data: list, date_func) -> list:
    """筛选本月的人品数据
    
    Args:
        data: 全部人品记录
        date_func: 日期过滤函数，判断是否为本月
        
    Returns:
        list: 本月的人品记录
    """
    return [item for item in data if date_func(item[2])]