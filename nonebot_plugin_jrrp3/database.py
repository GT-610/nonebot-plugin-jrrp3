import sqlite3
from nonebot.log import logger
from nonebot_plugin_localstore import get_plugin_data_dir
import datetime
from typing import List, Tuple

# 在标准数据目录下创建jrrp3子目录并设置数据库文件路径
plugin_data_dir = get_plugin_data_dir()
DB_PATH = plugin_data_dir / "jrrpdata.db"

# 确保数据目录存在
data_dir = DB_PATH.parent
data_dir.mkdir(parents=True, exist_ok=True)

logger.debug(f"数据库路径: {DB_PATH}")

# 数据库连接辅助函数
def get_db_connection() -> sqlite3.Connection:
    """获取数据库连接
    
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    conn = sqlite3.connect(str(DB_PATH))
    # 启用外键约束
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# 初始化数据库
def init_database() -> None:
    """初始化数据库表"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            create_tb_cmd = '''
            CREATE TABLE IF NOT EXISTS jdata
            (
                QQID INTEGER NOT NULL,
                Value INTEGER NOT NULL,
                Date TEXT NOT NULL,
                PRIMARY KEY (QQID, Date)
            );
            '''
            cursor.execute(create_tb_cmd)
            conn.commit()
        logger.info("数据库表初始化成功")
    except Exception as e:
        logger.error(f"数据库表初始化失败: {e}")

# 新增数据
def insert_tb(qqid: str, value: int, date: str) -> None:
    """向数据库插入新的人品记录
    
    Args:
        qqid: 用户ID
        value: 人品值
        date: 日期字符串
        
    Raises:
        Exception: 插入数据失败时抛出异常
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 使用参数化查询避免SQL注入
            insert_tb_cmd = 'INSERT OR IGNORE INTO jdata(QQID, Value, Date) VALUES(?, ?, ?)'
            cursor.execute(insert_tb_cmd, (qqid, value, date))
            conn.commit()
    except Exception as e:
        logger.error(f"插入数据失败: {e}")
        raise

# 查询历史数据
def select_tb_all(qqid: str) -> List[Tuple[str, int, str]]:
    """查询用户的所有历史人品记录
    
    Args:
        qqid: 用户ID
        
    Returns:
        List[Tuple[str, int, str]]: 历史记录列表，每个元素为(QQID, Value, Date)格式的元组
    """
    try:
        with get_db_connection() as conn:
            # 设置返回结果为字典格式
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            select_tb_cmd = 'SELECT QQID, Value, Date FROM jdata WHERE QQID = ? ORDER BY Date DESC'
            cursor.execute(select_tb_cmd, (qqid,))
            # 转换为元组列表返回
            return [(str(row['QQID']), int(row['Value']), str(row['Date'])) for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"查询历史数据失败: {e}")
        return []

# 查询今日是否存在数据
def select_tb_today(qqid: str, date: str) -> bool:
    """查询用户今日是否已经查询过人品
    
    Args:
        qqid: 用户ID
        date: 日期字符串
        
    Returns:
        bool: 如果今日已查询过返回True，否则返回False
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            select_tb_cmd = 'SELECT 1 FROM jdata WHERE QQID = ? AND Date = ? LIMIT 1'
            cursor.execute(select_tb_cmd, (qqid, date))
            return cursor.fetchone() is not None
    except Exception as e:
        logger.error(f"查询今日数据失败: {e}")
        return False

# 判断是否本周
def same_week(date_string: str) -> bool:
    """判断日期字符串是否为本周
    
    Args:
        date_string: 日期字符串，格式为'%y%m%d'
        
    Returns:
        bool: 如果日期在本周返回True，否则返回False
    """
    try:
        date_obj = datetime.datetime.strptime(date_string, '%y%m%d')
        today = datetime.datetime.today()
        # 检查是否为同一年的同一周
        return (date_obj.isocalendar()[1] == today.isocalendar()[1] and 
                date_obj.year == today.year)
    except ValueError:
        logger.error(f"日期格式错误: {date_string}")
        return False

# 判断是否本月
def same_month(date_string: str) -> bool:
    """判断日期字符串是否为本月
    
    Args:
        date_string: 日期字符串，格式为'%y%m%d'
        
    Returns:
        bool: 如果日期在本月返回True，否则返回False
    """
    try:
        date_obj = datetime.datetime.strptime(date_string, '%y%m%d')
        today = datetime.datetime.today()
        # 检查是否为同一年的同一月
        return (date_obj.month == today.month and 
                date_obj.year == today.year)
    except ValueError:
        logger.error(f"日期格式错误: {date_string}")
        return False