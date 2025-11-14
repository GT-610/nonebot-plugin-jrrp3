import sqlite3
from nonebot.log import logger
from nonebot_plugin_localstore import get_plugin_data_dir
import datetime

# 在标准数据目录下创建jrrp3子目录并设置数据库文件路径
plugin_data_dir = get_plugin_data_dir()
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