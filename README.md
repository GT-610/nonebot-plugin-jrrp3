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

一个功能完善的每日人品查询插件，支持查询今日、本周、本月和历史平均人品，自定义运势，以及数据持久化存储。

### 主要功能和特点
- 完全使用 Alconna 指令解析器重写逻辑，减少误触，增加反应速度
- 使用 Localstore 插件管理数据存储路径
- 完善的安全控制和异常处理
- 支持原 jrrp2 插件数据库无缝迁移
- 支持通过配置文件自定义运势范围和描述

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

### 数据存储配置

本插件使用 `nonebot_plugin_localstore` 自动管理数据存储路径，无需手动配置数据库路径。数据默认存储在 NoneBot 的标准插件数据目录。

> [!NOTE]
> 插件设计上兼容 nonebot_plugin_jrrp2 的数据库格式，您可以将原数据库文件直接复制到插件的数据目录中，实现数据迁移。

### 自定义运势配置

插件支持通过 YAML 配置文件自定义运势范围和描述。

配置文件路径如下：
```
$LOCALSTORE_CONFIG_DIR/nonebot_plugin_jrrp3/jrrp_config.yaml
```

首次运行插件的时候会自动生成配置文件。

#### 配置文件示例

完整的默认配置文件 `config/nonebot_plugin_jrrp3/jrrp_config.yaml` 如下：

```yaml
ranges:
- description: 100！100诶！！你就是欧皇？
  level: 超吉
  max: 100
  min: 100
- description: 好耶！今天运气真不错呢
  level: 大吉
  max: 99
  min: 76
- description: 哦豁，今天运气还顺利哦
  level: 吉
  max: 75
  min: 66
- description: emm，今天运气一般般呢
  level: 半吉
  max: 65
  min: 63
- description: 还……还行吧，今天运气稍差一点点呢
  level: 小吉
  max: 62
  min: 59
- description: 唔……今天运气有点差哦
  level: 末小吉
  max: 58
  min: 54
- description: 呜哇，今天运气应该不太好
  level: 末吉
  max: 53
  min: 19
- description: 啊这……(没错……是百分制)，今天还是吃点好的吧
  level: 凶
  max: 18
  min: 10
- description: 啊这……(个位数可还行)，今天还是吃点好的吧
  level: 大凶
  max: 9
  min: 1
- description: ？？？反向欧皇？
  level: 超凶（大寄）
  max: 0
  min: 0
```

#### 自定义配置示例

如果你想自定义运势范围，可以直接修改 `jrrp_config.yaml` 。例如：

```yaml
ranges:
  - min: 90
    max: 100
    level: "极佳"
    description: "今天你是天选之子！"
  - min: 70
    max: 89
    level: "很好"
    description: "今天运势不错哦～"
  - min: 50
    max: 69
    level: "一般"
    description: "平平无奇的一天"
  - min: 30
    max: 49
    level: "较差"
    description: "今天可能需要小心点"
  - min: 0
    max: 29
    level: "极差"
    description: "建议今天躺平休息"
```

#### 配置参数说明

- `ranges`：运势范围配置数组，每个元素定义一个运势等级的数值范围和描述
- `min`：该范围的最小值（包含）
- `max`：该范围的最大值（包含）
- `level`：运势等级名称
- `description`：运势描述文本

`min` `max` 范围严格遵循 Python `random.randint()` 的**左闭右闭**原则，即 `[min, max]` 包含两端边界值。

**注意事项：**

1. 范围配置中的数值应该连续且不重叠，确保每个可能的随机数都能匹配到唯一的运势等级
2. 配置文件会在插件加载时自动读取，如果配置文件不存在，将使用默认配置
3. 修改配置后，需要重启 Bot 才能生效（后期将增加热重载机制）

## 🎉 使用

### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| jrrp/今日人品/今日运势 | 群员 | 否 | 群聊/私聊 | 查询今日人品指数 |
| weekjrrp/本周人品/本周运势/周运势 | 群员 | 否 | 群聊/私聊 | 查询本周平均人品 |
| monthjrrp/本月人品/本月运势/月运势 | 群员 | 否 | 群聊/私聊 | 查询本月平均人品 |
| alljrrp/总人品/平均人品/平均运势 | 群员 | 否 | 群聊/私聊 | 查询历史平均人品 |

## 🧐 底层原理

- 随机数种子基于用户 ID 和当前日期，确保同一用户在同一天获得的幸运指数固定
- 随机数生成后会进行安全检查，防止生成超出合理范围的值

## 📦 依赖

- nonebot2 >= 2.3.0
- nonebot-plugin-alconna >= 0.50.0
- nonebot-plugin-localstore >= 0.6.0
- PyYAML >= 6.0
- Python >= 3.9, < 4.0

## 📝 许可证

本项目使用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。