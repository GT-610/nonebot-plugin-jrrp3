from nonebot import require, get_driver

require("nonebot_plugin_alconna")
require("nonebot_plugin_localstore")

driver = get_driver()

from nonebot_plugin_localstore import get_plugin_data_dir
from .database import init_database
from .command import register_commands
from .config import get_config

plugin_data_dir = get_plugin_data_dir()
plugin_data_dir.mkdir(parents=True, exist_ok=True)

from nonebot.plugin import PluginMetadata, inherit_supported_adapters

__plugin_meta__ = PluginMetadata(
    name="每日人品 3",
    description="更加现代化的 NoneBot2 每日人品插件，支持查询今日、本周、本月和历史平均人品，自定义运势，以及数据持久化存储。",
    usage="jrrp/今日人品/今日运势 - 查询今日人品指数\nweekjrrp/本周人品/本周运势/周运势 - 查询本周平均人品\nmonthjrrp/本月人品/本月运势/月运势 - 查询本月平均人品\nalljrrp/总人品/平均人品/平均运势 - 查询历史平均人品",
    type="application",
    homepage="https://github.com/GT-610/nonebot-plugin-jrrp3",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)

@driver.on_startup
async def startup():
    get_config()
    init_database()
    await register_commands()
