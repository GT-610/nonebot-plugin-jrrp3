from typing import Dict, Any, Tuple, Optional
import json
import yaml
from nonebot import logger
from nonebot_plugin_localstore import get_plugin_config_dir
from .constants import LuckValueBounds

class ConfigManager:
    _instance: Optional['ConfigManager'] = None
    _config: Optional[Dict[str, Any]] = None

    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._load_config()

    @classmethod
    def get_instance(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def config(self) -> Dict[str, Any]:
        if self._config is None:
            self._load_config()
        return self._config

    def _calculate_min_max_from_ranges(self, ranges_config: list) -> Tuple[int, int]:
        if not ranges_config or not isinstance(ranges_config, list):
            return LuckValueBounds.MIN_SAFE, LuckValueBounds.MAX_SAFE
        
        mins = []
        maxs = []
        
        for range_info in ranges_config:
            if isinstance(range_info, dict) and 'min' in range_info and 'max' in range_info:
                mins.append(range_info['min'])
                maxs.append(range_info['max'])
        
        if not mins or not maxs:
            return LuckValueBounds.MIN_SAFE, LuckValueBounds.MAX_SAFE
        
        return min(mins), max(maxs)

    def _apply_bounds_control(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        min_value = config_data.get("min_value", LuckValueBounds.MIN_SAFE)
        config_data["min_value"] = max(LuckValueBounds.MIN_SAFE, min_value)
        
        max_value = config_data.get("max_value", LuckValueBounds.MAX_SAFE)
        config_data["max_value"] = min(LuckValueBounds.MAX_SAFE, max_value)
        
        if config_data["max_value"] <= config_data["min_value"]:
            config_data["max_value"] = config_data["min_value"] + 1
            logger.warning("配置中max_value小于等于min_value，已自动调整")
        
        if "ranges" in config_data and isinstance(config_data["ranges"], list):
            min_luck, max_luck = self._calculate_min_max_from_ranges(config_data["ranges"])
            config_data["min_luck"] = min_luck
            config_data["max_luck"] = max_luck
        
        logger.info(f"最小运气值: {config_data.get('min_luck')}, 最大运气值：{config_data.get('max_luck') - 1}")
        return config_data

    def _validate_and_fix_ranges(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        if "ranges" not in config_data or not isinstance(config_data["ranges"], list):
            logger.warning("ranges配置无效或缺失，使用默认配置")
            config_data["ranges"] = DEFAULT_CONFIG["ranges"]
            return config_data
        
        ranges = config_data["ranges"]
        valid_ranges = []
        min_value = config_data.get("min_value", LuckValueBounds.MIN_SAFE)
        max_value = config_data.get("max_value", LuckValueBounds.MAX_SAFE)
        
        for range_info in ranges:
            if not isinstance(range_info, dict):
                logger.warning("范围配置项不是字典格式，跳过")
                continue
                
            required_fields = ["min", "max", "level", "description"]
            if not all(field in range_info for field in required_fields):
                logger.warning(f"范围配置项缺少必要字段，跳过")
                continue
                
            min_range = int(range_info["min"])
            max_range = int(range_info["max"])
            
            min_range = max(min_value, min_range)
            max_range = min(max_value, max_range)
            
            if max_range < min_range:
                max_range = min_range
                logger.warning(f"范围配置项的max小于min，已自动调整")
            
            valid_range = range_info.copy()
            valid_range["min"] = min_range
            valid_range["max"] = max_range
            valid_ranges.append(valid_range)
        
        if not valid_ranges:
            logger.warning("没有有效的范围配置，使用默认配置")
            config_data["ranges"] = DEFAULT_CONFIG["ranges"]
        else:
            config_data["ranges"] = valid_ranges
            logger.info(f"范围配置验证完成，共 {len(valid_ranges)} 个有效范围")
        
        return config_data

    def _load_config(self) -> None:
        config_dir = get_plugin_config_dir()
        
        config_dir.mkdir(parents=True, exist_ok=True)
        
        if config_file_path.exists() and json_config_file_path.exists():
            logger.warning("同时存在YAML和JSON配置文件，优先使用YAML配置文件")
        
        loaded_config = None
        
        if config_file_path.exists():
            try:
                with open(config_file_path, "r", encoding="utf-8") as file:
                    loaded_config = yaml.safe_load(file)
                if loaded_config:
                    logger.info(f"成功从YAML配置文件加载配置: {config_file_path}")
            except Exception as e:
                logger.error(f"从YAML配置文件加载配置失败: {e}")
        
        if loaded_config is None and json_config_file_path.exists():
            try:
                with open(json_config_file_path, "r", encoding="utf-8") as file:
                    loaded_config = json.load(file)
                if loaded_config:
                    logger.info(f"成功从JSON配置文件加载配置: {json_config_file_path}")
            except Exception as e:
                logger.error(f"从JSON配置文件加载配置失败: {e}")
        
        if loaded_config is None:
            logger.info("未找到配置文件，使用默认配置并创建YAML配置文件")
            loaded_config = DEFAULT_CONFIG.copy()
            
            if not isinstance(loaded_config, dict):
                logger.error("配置格式错误，使用默认配置")
                loaded_config = DEFAULT_CONFIG.copy()
            
            try:
                config_to_save = {}
                for key in DEFAULT_CONFIG:
                    if key in loaded_config:
                        config_to_save[key] = loaded_config[key]
                        
                with open(config_file_path, "w", encoding="utf-8") as file:
                    yaml.dump(config_to_save, file, allow_unicode=True)
                logger.info(f"成功创建默认YAML配置文件: {config_file_path}")
            except Exception as e:
                logger.error(f"创建默认YAML配置文件失败: {e}")
        
        loaded_config = self._validate_and_fix_ranges(loaded_config)
        loaded_config = self._apply_bounds_control(loaded_config)
        
        self._config = loaded_config

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def reload(self) -> None:
        self._config = None
        self._load_config()

plugin_config_dir = get_plugin_config_dir()
config_file_path = plugin_config_dir / "jrrp_config.yaml"
json_config_file_path = plugin_config_dir / "jrrp_config.json"

DEFAULT_CONFIG = {
    "ranges": [
        {"description": "100！100诶！！你就是欧皇？", "level": "超吉", "max": 100, "min": 100},
        {"description": "好耶！今天运气真不错呢", "level": "大吉", "max": 99, "min": 76},
        {"description": "哦豁，今天运气还顺利哦", "level": "吉", "max": 75, "min": 66},
        {"description": "emm，今天运气一般般呢", "level": "半吉", "max": 65, "min": 63},
        {"description": "还……还行吧，今天运气稍差一点点呢", "level": "小吉", "max": 62, "min": 59},
        {"description": "唔……今天运气有点差哦", "level": "末小吉", "max": 58, "min": 54},
        {"description": "呜哇，今天运气应该不太好", "level": "末吉", "max": 53, "min": 19},
        {"description": "啊这……（没错……是百分制），今天还是吃点好的吧", "level": "凶", "max": 18, "min": 10},
        {"description": "啊这……（个位数可还行），今天还是吃点好的吧", "level": "大凶", "max": 9, "min": 1},
        {"description": "？？？反向欧皇？", "level": "超凶（大寄）", "max": 0, "min": 0}
    ],
    "command": {
        "enable_jrrp": True,
        "enable_alljrrp": True,
        "enable_weekjrrp": True,
        "enable_monthjrrp": True
    }
}

def get_config() -> Dict[str, Any]:
    return ConfigManager.get_instance().config

def get_config_value(key: str, default: Any = None) -> Any:
    return ConfigManager.get_instance().get(key, default)

logger.debug(f"配置文件路径(YAML): {config_file_path}")
logger.debug(f"配置文件路径(JSON): {json_config_file_path}")
