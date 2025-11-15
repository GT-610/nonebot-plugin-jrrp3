from typing import Dict, Any, Tuple
import json
import yaml
from nonebot import logger
from nonebot.log import logger
from nonebot_plugin_localstore import get_plugin_config_dir

# 定义安全边界
MIN_SAFE_VALUE = 1
MAX_SAFE_VALUE = 100

# 配置文件路径
plugin_config_dir = get_plugin_config_dir()
config_file_path = plugin_config_dir / "jrrp_config.yaml"
json_config_file_path = plugin_config_dir / "jrrp_config.json"

# 全局配置变量
plugin_config = None

# 默认配置
DEFAULT_CONFIG = {
    # 基础配置
    "description": "jrrp3 插件配置",
    "version": "1.0.0",
    
    # 运势范围配置 - 使用列表格式，与YAML配置文件保持一致
    "ranges": [
        {"min": 1, "max": 20, "level": "极凶", "description": "今天运气极差"},
        {"min": 21, "max": 40, "level": "大凶", "description": "今天运气很差"},
        {"min": 41, "max": 50, "level": "凶", "description": "今天运气不太好"},
        {"min": 51, "max": 70, "level": "吉", "description": "今天运气不错"},
        {"min": 71, "max": 85, "level": "大吉", "description": "今天运气很好"},
        {"min": 86, "max": 100, "level": "极吉", "description": "今天运气极佳"}
    ],
    
    # 边界控制
    "min_value": MIN_SAFE_VALUE,
    "max_value": MAX_SAFE_VALUE,
    
    # 指令配置
    "command": {
        "enable_jrrp": True,
        "enable_alljrrp": True,
        "enable_weekjrrp": True,
        "enable_monthjrrp": True
    }
}

# 从范围配置计算实际最小值和最大值
def _calculate_min_max_from_ranges(ranges_config: list) -> Tuple[int, int]:
    """从运势范围配置中计算实际的最小值和最大值
    
    Args:
        ranges_config: 运势范围配置列表
        
    Returns:
        Tuple[int, int]: (实际最小值, 实际最大值)
    """
    if not ranges_config or not isinstance(ranges_config, list):
        return MIN_SAFE_VALUE, MAX_SAFE_VALUE
    
    # 收集所有范围的最小和最大值
    mins = []
    maxs = []
    
    for range_info in ranges_config:
        if isinstance(range_info, dict) and 'min' in range_info and 'max' in range_info:
            mins.append(range_info['min'])
            maxs.append(range_info['max'])
    
    if not mins or not maxs:
        return MIN_SAFE_VALUE, MAX_SAFE_VALUE
    
    # 返回最小的最小值和最大的最大值
    return min(mins), max(maxs)

# 应用边界控制
def _apply_bounds_control(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """确保配置中的值在安全范围内
    
    Args:
        config_data: 配置数据字典
        
    Returns:
        Dict[str, Any]: 经过边界控制后的配置数据
    """
    # 确保min_value在安全范围内
    min_value = config_data.get("min_value", MIN_SAFE_VALUE)
    config_data["min_value"] = max(MIN_SAFE_VALUE, min_value)
    
    # 确保max_value在安全范围内且大于min_value
    max_value = config_data.get("max_value", MAX_SAFE_VALUE)
    config_data["max_value"] = min(MAX_SAFE_VALUE, max_value)
    
    # 确保max_value大于min_value
    if config_data["max_value"] <= config_data["min_value"]:
        config_data["max_value"] = config_data["min_value"] + 1
        logger.warning("配置中max_value小于等于min_value，已自动调整")
    
    # 计算实际的最小/最大运气值
    if "ranges" in config_data and isinstance(config_data["ranges"], list):
        min_luck, max_luck = _calculate_min_max_from_ranges(config_data["ranges"])
        config_data["min_luck"] = min_luck
        config_data["max_luck"] = max_luck
    
    logger.info(f"配置边界控制已应用: min_value={config_data['min_value']}, max_value={config_data['max_value']}")
    return config_data

# 验证并修复范围配置
def _validate_and_fix_ranges(config_data):
    """验证并修复运势范围配置"""
    if "ranges" not in config_data or not isinstance(config_data["ranges"], list):
        logger.warning("ranges配置无效或缺失，使用默认配置")
        config_data["ranges"] = DEFAULT_CONFIG["ranges"]
        return config_data
    
    ranges = config_data["ranges"]
    valid_ranges = []
    min_value = config_data.get("min_value", MIN_SAFE_VALUE)
    max_value = config_data.get("max_value", MAX_SAFE_VALUE)
    
    # 验证每个范围配置
    for range_info in ranges:
        if not isinstance(range_info, dict):
            logger.warning("范围配置项不是字典格式，跳过")
            continue
            
        # 确保min、max和必要字段存在
        required_fields = ["min", "max", "level", "description"]
        if not all(field in range_info for field in required_fields):
            logger.warning(f"范围配置项缺少必要字段，跳过")
            continue
            
        # 转换为整数并限制在安全范围内
        min_range = int(range_info["min"])
        max_range = int(range_info["max"])
        
        # 应用边界控制
        min_range = max(min_value, min_range)
        max_range = min(max_value, max_range)
        
        # 确保max >= min
        if max_range < min_range:
            max_range = min_range
            logger.warning(f"范围配置项的max小于min，已自动调整")
            
        # 保留所有字段
        valid_range = range_info.copy()
        valid_range["min"] = min_range
        valid_range["max"] = max_range
        valid_ranges.append(valid_range)
    
    # 如果没有有效的范围配置，使用默认配置
    if not valid_ranges:
        logger.warning("没有有效的范围配置，使用默认配置")
        config_data["ranges"] = DEFAULT_CONFIG["ranges"]
    else:
        config_data["ranges"] = valid_ranges
        logger.info(f"范围配置验证完成，共 {len(valid_ranges)} 个有效范围")
    
    return config_data

def load_config():
    """加载配置文件，如果不存在则创建默认配置
    
    Returns:
        dict: 加载的配置字典
    """
    global plugin_config
    
    # 确保配置目录存在
    plugin_config_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查两种配置文件是否同时存在
    if config_file_path.exists() and json_config_file_path.exists():
        logger.warning("同时存在YAML和JSON配置文件，优先使用YAML配置文件")
    
    # 尝试加载YAML配置文件
    if config_file_path.exists():
        try:
            with open(config_file_path, "r", encoding="utf-8") as file:
                loaded_config = yaml.safe_load(file)
            if loaded_config:
                logger.info(f"成功从YAML配置文件加载配置: {config_file_path}")
                # 验证并修正配置
                loaded_config = _validate_and_fix_ranges(loaded_config)
                loaded_config = _apply_bounds_control(loaded_config)
                # 更新全局配置变量
                plugin_config = loaded_config
                return loaded_config
        except Exception as e:
            logger.error(f"从YAML配置文件加载配置失败: {e}")
    
    # 尝试加载JSON配置文件
    if json_config_file_path.exists():
        try:
            with open(json_config_file_path, "r", encoding="utf-8") as file:
                loaded_config = json.load(file)
            if loaded_config:
                logger.info(f"成功从JSON配置文件加载配置: {json_config_file_path}")
                # 验证并修正配置
                loaded_config = _validate_and_fix_ranges(loaded_config)
                loaded_config = _apply_bounds_control(loaded_config)
                # 更新全局配置变量
                plugin_config = loaded_config
                return loaded_config
        except Exception as e:
            logger.error(f"从JSON配置文件加载配置失败: {e}")
    
    # 如果都不存在，返回默认配置
    logger.info("未找到配置文件，使用默认配置")
    loaded_config = DEFAULT_CONFIG.copy()
    
    # 确保loaded_config是字典
    if not isinstance(loaded_config, dict):
        logger.error("配置格式错误，使用默认配置")
        loaded_config = DEFAULT_CONFIG.copy()
    
    # 验证并修正配置
    loaded_config = _validate_and_fix_ranges(loaded_config)
    loaded_config = _apply_bounds_control(loaded_config)
    
    # 更新全局配置变量
    plugin_config = loaded_config
    
    return loaded_config

def get_config():
    """获取当前配置
    
    Returns:
        dict: 当前配置字典
    """
    global plugin_config
    if plugin_config is None:
        load_config()
    return plugin_config

# 打印配置文件路径用于调试
logger.debug(f"配置文件路径(YAML): {config_file_path}")
logger.debug(f"配置文件路径(JSON): {json_config_file_path}")

# 全局配置变量
config = {}