<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/refs/heads/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/refs/heads/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-jrrp3

_✨ 更加现代化的 NoneBot2 每日人品插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/GT-610/nonebot_plugin_jrrp3.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot_plugin_jrrp3">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-jrrp3.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">
<a href="https://v2.nonebot.dev/">
    <img src="https://img.shields.io/badge/NoneBot-v2-green.svg" alt="NoneBot2">
</a>

</div>

## 📖 介绍

[nonebot_plugin_jrrp2](https://github.com/Rene8028/nonebot_plugin_jrrp2) 的现代化 Fork。

一个功能完善的每日人品查询插件，支持查询今日、本周、本月和历史平均人品，提供详细的运势评价，并支持数据持久化存储。

### 与 [nonebot_plugin_jrrp2](https://github.com/Rene8028/nonebot_plugin_jrrp2) 的区别
- 更加现代化的代码逻辑，减少误触和bug
- 持续维护与性能优化
- 完全兼容原插件数据库，支持无缝迁移

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-jrrp3

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-jrrp3
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-jrrp3
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-jrrp3
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-jrrp3
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot-plugin-jrrp3"] 

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| JRRP_DB_PATH | 否 | data/jrrp3/jrrpdata.db | 历史数据存储位置 |

> [!NOTE]
> 插件设计上兼容 nonebot_plugin_jrrp2 的数据库，因此您可以直接复制 nonebot_plugin_jrrp2 的数据库文件到新位置实现数据迁移。

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| jrrp/j/今日人品/今日运势 | 群员 | 否 | 群聊/私聊 | 查询今日人品指数 |
| 本周人品/本周运势/周运势 | 群员 | 否 | 群聊/私聊 | 查询本周平均人品 |
| 本月人品/本月运势/月运势 | 群员 | 否 | 群聊/私聊 | 查询本月平均人品 |
| 总人品/平均人品/平均运势 | 群员 | 否 | 群聊/私聊 | 查询历史平均人品 |

### 功能说明

1. **每日人品查询**：每天获得一个1-100的随机数作为今日幸运指数
2. **本周统计**：显示本周使用次数和平均幸运指数
3. **本月统计**：显示本月使用次数和平均幸运指数
4. **历史统计**：显示全部历史使用次数和平均幸运指数

### 运势等级划分

| 分数范围 | 评级 | 描述 |
|:-------:|:-----:|:----:|
| 0-20 | 大凶 | 今天不宜出门，诸事不顺 |
| 21-40 | 凶 | 今天运气不太好，小心行事 |
| 41-60 | 平 | 今天运气一般，平常心对待 |
| 61-80 | 吉 | 今天运气不错，适合做重要的事情 |
| 81-99 | 大吉 | 今天运气很好，是个好日子 |
| 100 | 欧皇 | 恭喜！今天你就是欧皇本人！ |

## 📦 依赖

- nonebot2 >= 2.0.0
- nonebot-plugin-saa >= 0.3.2
- Python >= 3.9

## 📝 许可证

本项目使用 MIT 许可证，详详见 [LICENSE](LICENSE) 文件。