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

### 与 nonebot-plugin-jrrp2 的区别
- 完全使用 Alconna 指令解析器重写逻辑，减少误触，增加反应速度
- 使用 localstore 插件存储数据存储路径。
- 完善的错误处理和异常捕获
- 支持原jrrp2插件数据库迁移

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

本插件使用 `nonebot_plugin_localstore` 自动管理数据存储路径，无需手动配置数据库路径。数据默认存储在 NoneBot 的标准插件数据目录。

> [!NOTE]
> 插件设计上兼容 nonebot_plugin_jrrp2 的数据库格式，您可以将原数据库文件直接复制到插件的数据目录中，实现数据迁移。

## 🎉 使用
### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| jrrp/今日人品/今日运势 | 群员 | 否 | 群聊/私聊 | 查询今日人品指数 |
| weekjrrp/本周人品/本周运势/周运势 | 群员 | 否 | 群聊/私聊 | 查询本周平均人品 |
| monthjrrp/本月人品/本月运势/月运势 | 群员 | 否 | 群聊/私聊 | 查询本月平均人品 |
| alljrrp/总人品/平均人品/平均运势 | 群员 | 否 | 群聊/私聊 | 查询历史平均人品 |

### 功能说明

1. **每日人品查询**：每天获得一个1-100的随机数作为今日幸运指数
2. **本周统计**：显示本周使用次数和平均幸运指数
3. **本月统计**：显示本月使用次数和平均幸运指数
4. **历史统计**：显示全部历史使用次数和平均幸运指数

### 运势等级划分

当前运势等级与 `nonebot-plugin-jrrp2` 保持一致，且固定在代码中。后期会增加自定义运势范围和内容的功能。


| 分数 | 评级 | 描述 |
|:-------:|:-----:|:----:|
| 100 | 超吉 | 100！100诶！！你就是欧皇？ |
| 76-99 | 大吉 | 好耶！今天运气真不错呢 |
| 66-75 | 吉 | 哦豁，今天运气还顺利哦 |
| 63-65 | 半吉 | emm，今天运气一般般呢 |
| 59-62 | 小吉 | 还……还行吧，今天运气稍差一点点呢 |
| 54-58 | 末小吉 | 唔……今天运气有点差哦 |
| 10-53 | 末吉 | 呜哇，今天运气应该不太好 |
| 1-9 | 凶 | 啊这……(没错……是百分制)，今天还是吃点好的吧 |
| 0 | 大凶 | 啊这……(个位数可还行)，今天还是吃点好的吧 |

## 📦 依赖

- nonebot2 >= 2.3.0
- nonebot-plugin-alconna >= 0.50.0
- nonebot-plugin-localstore >= 0.6.0
- Python >= 3.9, < 4.0

## 📝 许可证

本项目使用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。