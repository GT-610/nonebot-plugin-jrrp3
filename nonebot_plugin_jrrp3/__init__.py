import json
import yaml
from nonebot import require, get_driver

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")

# 获取驱动
driver = get_driver()

from nonebot.log import logger
from nonebot_plugin_localstore import get_plugin_config_dir, get_plugin_data_dir
from .database import init_database
from .command import register_commands

# 使用nonebot-plugin-localstore获取标准配置存储路径
plugin_config_dir = get_plugin_config_dir()
# 使用nonebot-plugin-localstore获取标准数据存储路径
plugin_data_dir = get_plugin_data_dir()

# 配置文件路径
CONFIG_FILE_YAML = plugin_config_dir / "jrrp_config.yaml"
CONFIG_FILE_JSON = plugin_config_dir / "jrrp_config.json"
# 确保配置目录存在
plugin_config_dir.mkdir(parents=True, exist_ok=True)

# 默认配置（前闭后开）
DEFAULT_CONFIG = {
    "ranges": [
        {
            "min": 100,
            "max": 101,
            "level": "超吉",
            "description": "100！100诶！！你就是欧皇？"
        },
        {
            "min": 76,
            "max": 100,
            "level": "大吉",
            "description": "好耶！今天运气真不错呢"
        },
        {
            "min": 66,
            "max": 76,
            "level": "吉",
            "description": "哦豁，今天运气还顺利哦"
        },
        {
            "min": 63,
            "max": 66,
            "level": "半吉",
            "description": "emm，今天运气一般般呢"
        },
        {
            "min": 59,
            "max": 63,
            "level": "小吉",
            "description": "还……还行吧，今天运气稍差一点点呢"
        },
        {
            "min": 54,
            "max": 59,
            "level": "末小吉",
            "description": "唔……今天运气有点差哦"
        },
        {
            "min": 19,
            "max": 54,
            "level": "末吉",
            "description": "呜哇，今天运气应该不太好"
        },
        {
            "min": 10,
            "max": 19,
            "level": "凶",
            "description": "啊这……（没错……是百分制），今天还是吃点好的吧"
        },
        {
            "min": 1,
            "max": 10,
            "level": "大凶",
            "description": "啊这……（个位数可还行），今天还是吃点好的吧"
        },
        {
            "min": 0,
            "max": 1,
            "level": "超凶（大寄）",
            "description": "？？？反向欧皇？"
        }
    ]
}

# 全局配置变量
plugin_config = None

# 插件元数据
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

__plugin_meta__ = PluginMetadata(
    name="每日人品 3",
    description="更加现代化的 NoneBot2 每日人品插件，支持查询今日、本周、本月和历史平均人品，自定义运势，以及数据持久化存储。",
    usage="jrrp/今日人品/今日运势 - 查询今日人品指数\nweekjrrp/本周人品/本周运势/周运势 - 查询本周平均人品\nmonthjrrp/本月人品/本月运势/月运势 - 查询本月平均人品\nalljrrp/总人品/平均人品/平均运势 - 查询历史平均人品",

    type="application",
    # 发布必填，当前有效类型有：`library`（为其他插件编写提供功能），`application`（向机器人用户提供功能）。

    homepage="https://github.com/GT-610/nonebot-plugin-jrrp3",
    # 发布必填。

    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    # 使用 inherit_supported_adapters 从 alconna 插件继承支持的适配器
)


logger.debug(f"配置文件路径(YAML): {CONFIG_FILE_YAML}")
logger.debug(f"配置文件路径(JSON): {CONFIG_FILE_JSON}")

# 安全边界定义
MIN_SAFE_VALUE = -999999999
MAX_SAFE_VALUE = 999999999

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
        except Exception as e:
            logger.error(f"加载YAML配置文件失败: {e}")
            plugin_config = DEFAULT_CONFIG.copy()
            # 如果YAML加载失败，尝试JSON
            try:
                with open(CONFIG_FILE_JSON, 'r', encoding='utf-8') as f:
                    plugin_config = json.load(f)
                logger.warning(f"YAML加载失败，尝试加载JSON配置文件: {CONFIG_FILE_JSON}")
            except Exception as e:
                logger.error(f"加载JSON配置文件失败: {e}")
                plugin_config = DEFAULT_CONFIG.copy()
    
    # 如果只有一种格式存在，加载对应格式
    elif CONFIG_FILE_YAML.exists():
        try:
            with open(CONFIG_FILE_YAML, 'r', encoding='utf-8') as f:
                plugin_config = yaml.safe_load(f)
            logger.info(f"成功加载YAML配置文件: {CONFIG_FILE_YAML}")
        except Exception as e:
            logger.error(f"加载YAML配置文件失败: {e}")
            plugin_config = DEFAULT_CONFIG.copy()
    
    elif CONFIG_FILE_JSON.exists():
        try:
            with open(CONFIG_FILE_JSON, 'r', encoding='utf-8') as f:
                plugin_config = json.load(f)
            logger.info(f"成功加载JSON配置文件: {CONFIG_FILE_JSON}")
        except Exception as e:
            logger.error(f"加载JSON配置文件失败: {e}")
            plugin_config = DEFAULT_CONFIG.copy()
    
    # 如果都不存在，创建默认YAML配置文件
    else:
        try:
            with open(CONFIG_FILE_YAML, 'w', encoding='utf-8') as f:
                yaml.dump(DEFAULT_CONFIG, f, allow_unicode=True, default_flow_style=False)
            plugin_config = DEFAULT_CONFIG.copy()
            logger.info(f"创建默认YAML配置文件: {CONFIG_FILE_YAML}")
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {e}")
            # 如果创建配置文件失败，使用内存中的默认配置
            plugin_config = DEFAULT_CONFIG.copy()
            logger.warning("使用内存中的默认配置")
    
    # 确保plugin_config是字典
    if not isinstance(plugin_config, dict):
        logger.error("配置文件格式错误，使用默认配置")
        plugin_config = DEFAULT_CONFIG.copy()
    
    # 确保ranges列表存在且格式正确
    if "ranges" not in plugin_config or not isinstance(plugin_config["ranges"], list):
        plugin_config["ranges"] = DEFAULT_CONFIG["ranges"]
    
    # 验证并修正ranges配置
    validate_and_fix_ranges()
    
    # 从ranges自动计算min_luck和max_luck
    calculate_min_max_from_ranges()
    
    # 应用边界控制（现在min_luck和max_luck已经被计算出来）
    apply_bounds_control()
    

def calculate_min_max_from_ranges():
    """从ranges配置中自动计算最小和最大运气值"""
    global plugin_config
    
    if not plugin_config.get("ranges"):
        logger.error("ranges配置为空，无法计算min_luck和max_luck")
        plugin_config["min_luck"] = 1
        plugin_config["max_luck"] = 100
        return
    
    # 收集所有min值和max值
    min_values = []
    max_values = []
    
    for range_config in plugin_config["ranges"]:
        if "min" in range_config:
            min_values.append(range_config["min"])
        if "max" in range_config:
            max_values.append(range_config["max"])
    
    if min_values and max_values:
        # 计算最小和最大值
        plugin_config["min_luck"] = min(min_values)
        plugin_config["max_luck"] = max(max_values)
        logger.info(f"从ranges自动计算得到: min_luck={plugin_config['min_luck']}, max_luck={plugin_config['max_luck']-1}")
    else:
        logger.warning("无法从ranges计算min_luck和max_luck，使用默认值")
        plugin_config["min_luck"] = 1
        plugin_config["max_luck"] = 101

def apply_bounds_control():
    """应用边界控制，确保配置值在安全范围内"""
    global plugin_config
    
    # min_luck和max_luck现在是从ranges自动计算的，不再需要单独处理
    pass
    
    # 确保min_luck <= max_luck
    if plugin_config["min_luck"] > plugin_config["max_luck"]:
        plugin_config["min_luck"], plugin_config["max_luck"] = plugin_config["max_luck"], plugin_config["min_luck"]
        logger.warning("min_luck大于max_luck，已自动交换")

def validate_and_fix_ranges():
    """验证并修正ranges配置，确保所有范围值在安全范围内"""
    global plugin_config
    ranges = plugin_config["ranges"]
    
    for i, range_config in enumerate(ranges):
        if not isinstance(range_config, dict):
            logger.warning(f"范围配置 #{i+1} 格式错误，已跳过")
            continue
        
        # 验证并修正min值
        if "min" in range_config:
            try:
                min_val = int(range_config["min"])
                # 确保在安全范围内
                if min_val < MIN_SAFE_VALUE or min_val > MAX_SAFE_VALUE:
                    logger.warning(f"范围 #{i+1} 的min值 {min_val} 超出安全范围，已修正")
                    min_val = max(MIN_SAFE_VALUE, min(min_val, MAX_SAFE_VALUE))
                range_config["min"] = min_val
            except (ValueError, TypeError):
                logger.warning(f"范围 #{i+1} 的min值格式错误，已设为默认值")
                range_config["min"] = 0
        else:
            range_config["min"] = 0
        
        # 验证并修正max值
        if "max" in range_config:
            try:
                max_val = int(range_config["max"])
                # 确保在安全范围内
                if max_val < MIN_SAFE_VALUE or max_val > MAX_SAFE_VALUE:
                    logger.warning(f"范围 #{i+1} 的max值 {max_val} 超出安全范围，已修正")
                    max_val = max(MIN_SAFE_VALUE, min(max_val, MAX_SAFE_VALUE))
                range_config["max"] = max_val
            except (ValueError, TypeError):
                logger.warning(f"范围 #{i+1} 的max值格式错误，已设为默认值")
                range_config["max"] = 100
        else:
            range_config["max"] = 100
        
        # 确保min <= max (对于前闭后开区间，允许min == max)
        if range_config["min"] > range_config["max"]:
            range_config["min"], range_config["max"] = range_config["max"], range_config["min"]
            logger.warning(f"范围 #{i+1} 的min值大于max值，已自动交换")
        
        # 确保必要的字段存在
        if "level" not in range_config:
            range_config["level"] = "未知"
        if "description" not in range_config:
            range_config["description"] = "暂无描述"



# 在驱动启动时初始化数据库、加载配置并注册命令
@driver.on_startup
async def startup():
    load_config()
    init_database()
    await register_commands(plugin_config)

# 命令定义已迁移到command.py模块

# 处理函数已迁移到command.py模块

# 处理函数已迁移到command.py模块

# 处理函数已迁移到command.py模块

# 处理函数已迁移到command.py模块
