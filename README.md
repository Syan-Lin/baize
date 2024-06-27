
![img](banner.png)

<p align="center">
  <a href="https://github.com/Syan-Lin/baize/stargazers"><img src="https://img.shields.io/github/stars/Syan-Lin/baize?color=green&amp;logo=github&amp;style=for-the-badge" alt="Github stars"></a>
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=Python&logoColor=white&color=green" alt="Python">
  <a href="./LICENSE"><img src="https://img.shields.io/github/license/Syan-Lin/baize?&amp;color=green&amp;style=for-the-badge" alt="License"></a>
</p>

# 简介
baize 是一个将 LLM 能力集成至 Terminal 终端的工具框架，支持多种 LLM 模型和接口，并提供一系列终端命令，让用户能够方便地使用 LLM 能力。

> 白泽（baize）是中国古代神话中的瑞兽。能言语，通万物之情，知鬼神之事。

由于 LLM 调用价格被打下来了（百万 Token 低至几毛钱），使得个人使用 API 的成本迅速降低，让 LLM 可以真正高度定制化地接入到个人工作和生活的方方面面，baize 就是在这一背景下提出的。

目前支持的 LLM 接口：支持多家平台，可以让大家薅尽羊毛~
- [通义千问](https://bailian.console.aliyun.com/)
- [智谱 AI](https://open.bigmodel.cn/)
- [DeepSeek](https://platform.deepseek.com/)
- [豆包](https://www.volcengine.com/product/doubao)
- [OpenAI](https://platform.openai.com/)
- [月之暗面](https://platform.moonshot.cn/)

# 为什么需要 baize

简而言之，在终端中集成方便的 LLM 是一个刚需：

- 在终端的工作环境下，来回切换浏览器和 LLM 进行交互的效率低
- 无法方便地将 LLM 的能力集成至 Shell 脚本中

第一点意味着与 LLM 的交互效率提高，在日常工作中提高我们的工作效率；第二点则意味着，一些之前较复杂的任务可以基于 LLM 能力的脚本实现自动化，存在无限的想象力。除了这两点之外，baize 还提供了其他零碎场景的解决方案，等待大家自行探索！

基于终端的交互逻辑，我们的理念是让 baize 的交互和普通的 Linux 命令一样尽可能轻松，每次调用几乎只需要输入一个命令，就可以得到想要的结果。在这样的考虑下，baize 大部分的功能都相对较「底层」，具有一定的上手门槛，但像其他终端命令一样，一旦上手，baize 就能成为你随处可用的「瑞士军刀」！

**如果你的工作和生活经常用到终端，那么 baize 就是你需要的！**

# 安装

1. 克隆本仓库

```bash
git clone https://github.com/Syan-Lin/baize
```

2. 进入项目目录并安装依赖

```bash
cd baize
pip install -r requirements.txt
```

> 请你确保你的 Python 版本 >= 3.12，你可以通过 conda、venv 等工具来创建一个虚拟环境进行安装

3. 构建二进制程序

```bash
python install.py
```

4. 添加系统路径

目前支持 Linux 和 Mac 下的 bash 和 zsh，Windows 需要手动添加系统路径

```bash
# 如果你用的是 bash
~/baize/baize --init bash
# 如果你用的是 zsh
~/baize/baize --init zsh
```

5. 检查安装

```bash
# 如果正常输出版本信息，则代表安装成功
baize --version
```

# 快速开始
首次运行需要先进行模型的配置，配置文件在 `baize/config.yaml` 中，之后你可以再次运行 `baize --setup` 添加配置

```bash
baize --setup
```

对于商用模型来说，API KEY 是必须的配置；如果是本地部署或内部模型，BASE URL 是必须的配置，你可以通过 `baize --modellist` 查看当前已配置的模型

## 与 LLM 交互
### 最简单的交互方式

```bash
baize 你好
```

你可以通过 `--stream -s` 参数来开启流式输出

```bash
baize 你好 -s
```

### Prompt 模板

假定一个 Prompt 模板叫做 `example` 如下，其存放在 `baize/templates` 目录下：

```markdown
我叫 {}，今年 {} 岁，请你推荐几本书给我
```

通过 `--template -t` 参数，可以对 Prompt 模板进行格式化，从而很方便地调用各种模板

```bash
baize 你好 8 -t example
```

你可以通过 `baize --list` 查看当前可用的模板。

### 管道连接

管道连接是终端里面一个重要的概念，通过支持管道连接，对于简单的工作流，我们可以非常快捷地接起来

假设存在一个对文本进行总结的 Prompt 模板叫 `summary`，并且当前目录下存在一个叫 `book.txt` 的文本

```bash
cat book.txt | baize -t summary
```

当然你也可以构建更复杂的流程，将总结再翻译成英文并保存下来

```bash
cat book.txt | baize -t summary | baize -t trans2eng -o eng.txt
```

聪明的你一定一下就能想到如何将这个用法结合到自己的工作生活中，例如自动生成 commit message

```bash
git add .
git diff HEAD | baize -t commit
```

或者自动总结网页内容

```bash
curl https://www.example.com | baize -t summary -o webpage_summary.txt
```

### 多模态

对于多模态模型，baize 也提供了对应的功能，通过 `--file -f` 上传文本文件，`--img -i` 上传图片

```bash
baize 总结一下这篇文章 -f book.txt
baize 这个图片的内容是什么 -i cat.png
```

### 历史对话记录

在一些使用场景下，我们希望历史的对话记录得到保留，我们可以通过 `--previous -p` 来引入上一次的对话记录，连续使用可以连续保留多次记录，直到下一次不使用该参数调用为止，此时历史记录会清空

```bash
baize 你好
baize 我上一句话说了什么 -p
baize 我们说了几句话 -p
# 会清空之前的对话记录
baize 你好
```

你可以使用 `--log` 来查看详细的调用过程

```bash
baize 你好 -p --log
```

## 命令行模式
在终端中使用 LLM 的一大场景就是构造一个命令行命令，在传统的交互逻辑中，我们需要将 LLM 的输出从其他地方复制到终端中，而 baize 则提供了一种更优雅的方式，即命令行模式。通过 `--cli -c` 打开，该参数下，模型会直接给出命令。如果你想要详细的命令解释，你可以使用 `--clidetail` 参数，该参数下，模型会给出详细的命令解释

```bash
baize -c 在 main.py 文件中找到字符串 name，并打印出行号
`grep -n 'name' main.py` 是否执行 [y/n]:
```

如果是在详细模式下，LLM 则会具体解释

```bash
baize --clidetail 在 main.py 文件中找到字符串 name，并打印出行号
# 命令行命令：grep
## 介绍
`grep` 是一个强大的文本搜索工具，它使用正则表达式搜索包含指定模式的字符串，并显示匹配的行。

## 语法
grep [options] pattern [file...]

## 常用选项
- `-n`：显示匹配行及其行号。
- `-i`：忽略大小写。
- `-v`：反转匹配，即显示不包含模式的行。
- `-c`：计数，只输出匹配行的数量。

确保在使用 `grep` 命令时理解其参数和选项，以便能有效地进行文本搜索和过滤。
`grep -n "name" main.py` 是否执行 [y/n]:
```

## 工作流模式
工作流能够自定义一个简单的 LLM 交互流程，通过 `--workflow -w` 来指定一个预定义的工作流执行。工作流是一个由节点定义的有向无环图的流程结构，其中节点包括「输入节点」、「LLM 节点」、「Python 脚本节点」、「输出节点」，通过将这些节点组合成一个流程来实现一些复杂任务的自动化

工作流的流程目前需要手动配置

```bash
baize -w example
请输入参数 prompt: 生成一首诗

秋风起，黄叶飘，
寂寥世界，诗意渺。
月挂梢头，霜满地，
独行人影，长桥倒。
```

示例的背后实际上定义了一个并行结构，对于输入的 `prompt`，会有两个「LLM 节点」同时生成一首诗，接着再有一个「LLM 节点」来判断哪一首诗更好，输出更好的那首诗

## 工具模式
工具模式基于 function call 功能，使 baize 具有一定 Agent 的能力，例如调用一些预定义的接口，如天气查询、航班查询等。使 baize 可以执行现实中的动作，帮助我们解决一些简单的实际问题。考虑到目前各家大模型 Agent 的能力差异较大，需要能力较强的大模型才能很好地执行工具模式

通过 `--tool` 来指定一个预定义的工具执行，工具所对应的代码和调用接口目前需要手动配置

```bash
# interpreter 是 Python 解释器，可以执行大模型输出的代码
baize --tool interpreter --log
> 使用牛顿迭代法计算 x^3 = 5 的解
正在调用 `exec_code`

exec_code(code="""def newton_iteration(x0, iterations=10):
    x = x0
    for _ in range(iterations):
        x = x - (x**3 - 5) / (3 * x**2)
    return x

initial_guess = 1
iterations = 10
result = newton_iteration(initial_guess, iterations)
print(result)""")

{'stdout': '1.709975946676697\n', 'stderr': ''}

使用牛顿迭代法计算 x^3 = 5 的解为 x ≈ 1.70998。

# weather 是天气查询工具，定义了获取当前日期和根据日期、地点查询未来七天天气的函数
baize --tool weather --log
> 查询今天上海的天气
正在调用 `get_current_date`

get_current_date()

2024-06-24
正在调用 `get_weather`

get_weather(city="""上海""",date="""2024-06-24""")

{'reason': '查询成功!', 'result': {'city': '上海', 'realtime': {'temperature': '23', 'humidity': '96', 'info': '中雨', 'wid': '08', 'direct': '北风', 'power': '0级', 'aqi': '19'}, 'future': [{'date': '2024-06-27', 'temperature':
'23/25℃', 'weather': '中雨', 'wid': {'day': '08', 'night': '08'}, 'direct': '持续无风向'}, {'date': '2024-06-28', 'temperature': '24/27℃', 'weather': '小雨', 'wid': {'day': '07', 'night': '07'}, 'direct': '持续无风向'}, {'date':
'2024-06-29', 'temperature': '26/31℃', 'weather': '阴转小雨', 'wid': {'day': '02', 'night': '07'}, 'direct': '持续无风向'}, {'date': '2024-06-30', 'temperature': '26/31℃', 'weather': '小雨', 'wid': {'day': '07', 'night': '07'},
'direct': '持续无风向'}, {'date': '2024-07-01', 'temperature': '26/32℃', 'weather': '中雨转小雨', 'wid': {'day': '08', 'night': '07'}, 'direct': '持续无风向'}]}, 'error_code': 0}

根据查询结果，2024年6月27日上海的天气情况如下：温度为23/25℃，天气状况为中雨，风向为持续无风向。请注意，由于是中雨天气，建议您当天外出时准备好雨具。
```


## Prompt 配置

可以通过 `--createtemplate` 创建模板，但是需要注意，模板是通过 `{}` 进行格式化的，如果有正常文本中的 `{}`，请转义成 `{{}}`

### 设置上下文
Context 是一个对用户进行描述的系统 Prompt，你可以在这里定义你的背景信息和希望得到的回答是什么，可以更好地与 LLM 对齐

```bash
baize --setcontext 我是一个程序员
```

通过 `--setcontext` 就可以设置一个 Context，这个设置是全局生效的，之后每次调用 LLM 都会附带这个 Context

你可以通过 `--context` 查看当前所用的 Context；通过 `--resetcontext` 删除当前的 Context

```bash
baize --context
baize --resetcontext
```

## 更好的输入输出
### 从剪贴板获取输入
在命令行中工作时，有时候直接复制粘贴大段的文本，会使终端看起来很「脏」，这个时候可以使用 `--paste -P` 直接将剪贴板的内容作为输入

```bash
baize -P
```

### 输出到剪贴板
在命令行中工作时，有时候需要复制 LLM 的输出，这个时候可以通过 `--copy -C` 直接将模型的输出复制到剪贴板中

```bash
baize 请你给我一个 C++ 的快排实现 -C
```

### 输出到文件
在一些应用场景中，我们可以使 LLM 的输出直接保存到一个目录下，例如可以实现文章的自动总结，并保存到我们的笔记目录下

```bash
cat book.txt | baize -t summary -o ~/obsidian/summary.md
```

### Markdown 输出
baize 支持在终端中渲染 Markdown，包含代码样式，你可以通过 `--markdown -M` 开启该功能，支持流式输出的 Markdown 渲染

```bash
baize 请你给我一个C++的快排实现 -M
```

## 其他
你可以使用 `baize --help` 查看所有命令和选项