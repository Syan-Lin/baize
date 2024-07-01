
![img](banner.png)

<p align="center">
  <a href="https://github.com/Syan-Lin/baize/stargazers"><img src="https://img.shields.io/github/stars/Syan-Lin/baize?color=green&amp;logo=github&amp;style=for-the-badge" alt="Github stars"></a>
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=Python&logoColor=white&color=green" alt="Python">
  <a href="./LICENSE"><img src="https://img.shields.io/github/license/Syan-Lin/baize?&amp;color=green&amp;style=for-the-badge" alt="License"></a>
</p>

# 简介
baize 是一个将大模型集成至终端的工具框架，提供一系列方便的交互模式，提高在终端中使用大模型的效率

> 白泽（baize）是中国古代神话中的瑞兽。能言语，通万物之情，知鬼神之事。

由于大模型调用价格被打下来了（百万 Token 低至几毛钱），使得个人使用 API 的成本迅速降低，让大模型可以真正高度定制化地接入到个人工作和生活的方方面面，baize 就是在这一背景下提出的

目前支持的接口：支持多家平台和本地部署，可以让大家薅尽羊毛~
- [通义千问](https://bailian.console.aliyun.com/)
- [智谱 AI](https://open.bigmodel.cn/)
- [DeepSeek](https://platform.deepseek.com/)
- [豆包](https://www.volcengine.com/product/doubao)
- [OpenAI](https://platform.openai.com/)
- [月之暗面](https://platform.moonshot.cn/)
- [Ollama](https://github.com/ollama/ollama)

https://github.com/Syan-Lin/baize/assets/57340079/dae3b8f4-92bc-493f-b6ca-4b6790870dc8

# 为什么需要 baize

简而言之，在终端中集成大模型是一个刚需，目前存在以下局限：

- 在终端的工作环境下，来回切换浏览器或其他 APP 与大模型交互的效率低
- 无法利用大模型构建自动化任务，即无法方便地在 Shell 脚本中使用大模型

解决第一点意味着能够利用大模型提高终端工作环境下的效率；解决第二点意味着可以基于大模型实现一些复杂任务的自动化，存在无限的想象力。除了这两点之外，baize 还提供了其他零碎场景的解决方案，等待大家自行探索！

基于终端的交互逻辑，我们的理念是让 baize 和普通的终端命令一样尽可能简单，每次调用几乎只需要输入一个命令。在这样的考虑下，baize 大部分的功能都相对较「底层」，具有一定的上手门槛，需要对大模型有一定的了解，但像其他终端命令一样，一旦上手，baize 就能成为你随处可用的「瑞士军刀」！

**如果你的工作和生活经常用到终端，那么 baize 就是你需要的！**

# 安装

可以直接下载可执行文件也可以手动编译

## 下载可执行文件

1. 在 [release](https://github.com/Syan-Lin/baize/releases) 中下载对应的压缩包

2. 创建目录并解压

```bash
mkdir -p ~/.baize
tar -xzf <下载的文件名> -C ~/.baize
```

> Windows 需要手动进行以上操作

## 手动编译

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

3. 构建可执行程序

```bash
python install.py
```

## 添加系统路径

目前支持 Linux 和 Mac 下的 bash 和 zsh，Windows 需要手动添加系统路径

```bash
# 如果你用的是 bash
~/.baize/baize --init bash
# 如果你用的是 zsh
~/.baize/baize --init zsh
```

## 检查安装

```bash
# 如果正常输出版本信息，则代表安装成功
baize --version
```

# 快速开始
首次运行需要先进行模型的配置，之后你可以再次运行 `setup` 添加配置，通过 `modellist` 查看当前已配置的模型

```bash
# 模型配置
baize --setup
# 查看模型配置
baize --modellist
```

## 大模型交互
### 最简单的交互方式

```bash
baize 你好
```

你可以通过 `--stream -s` 参数来开启流式输出

```bash
baize 你好 -s
```

### 使用 Prompt 模板

通过 `--template -t` 参数，可以将输入和 Prompt 模板进行拼接，通过 `--list -l` 查看可用的模板

```bash
# 查看可用模板
baize -l
# acatrans 是一个用于学术中译英的 Prompt 模板
baize 深度学习有着广泛的应用 -t acatrans
```

对于模板还有以下操作：
- 创建模板：`--createtemplate`
- 查看模板内容：`--showtemplate <template>`
- 删除模板：`--deletetemplate <template>`

### 终端命令组合

终端命令组合是通过管道连接的方式实现的，管道连接是终端里面一个重要的概念，可以将多个命令组成一个 Pipeline 实现更复杂的任务

```bash
# 对文件进行总结再翻译成中文
cat book.txt | baize -t summary | baize -t acatrans
# 根据 diff 生成 commit
git diff HEAD | baize -t commit
# 获取网页内容总结
curl https://www.example.com | baize -t summary
```

### 多模态

对于多模态模型，baize 也提供了对应的功能，通过 `--file -f` 上传文本文件，`--img -i` 上传图片

```bash
# 文件支持一次上传多个
baize 总结一下这两篇文章 -f book.txt book2.txt
# 图片只有少数模型支持，是否可以上传多个由模型决定
baize 这个图片的内容是什么 -i cat.png
```

文件上传功能还可以与 Prompt 模板和管道组合，实现单文件的自动 Debug：

```bash
python example.py 2>&1 | baize 基于所给的文件及其输出信息，请你修复这个错误 -f example.py
```

### 历史上下文

在一些使用场景下，我们希望历史的对话留存在上下文中，可以通过 `--previous -p` 来引入上一次的对话记录，连续使用可以持续保留，直到下一次不使用该参数为止，此时历史对话会清空，可以通过 `-H` 来查看目前的历史上下文

```bash
baize 你好
baize 我上一句话说了什么 -p
baize -H
# 会清空之前的对话记录
baize 你好
```

## 更好的输入输出
### 从剪贴板获取输入
在命令行中工作时，有时候直接复制粘贴大段的文本，会使终端看起来很「脏」，或者导致命令解析错误，这个时候可以使用 `--paste -P` 直接将剪贴板的内容作为输入

```bash
baize -P
# 可以组合正常输入
baize 请你总结以下内容 -P
```

### 输出到剪贴板
在命令行中工作时，有时候需要复制大模型的输出，这个时候可以通过 `--copy -C` 直接将模型的输出复制到剪贴板中

```bash
baize 请你给我一个 C++ 的快排实现 -C
```

### 输出到文件
在一些应用场景中，我们可以使大模型的输出直接保存到一个目录下，例如可以将文章的总结保存到我们的笔记目录下

```bash
cat book.txt | baize -t summary -o ~/obsidian/summary.md
```

### Markdown 输出
baize 支持在终端中渲染 Markdown，包含代码样式，你可以通过 `--markdown -M` 开启该功能，支持流式输出的 Markdown 渲染

```bash
baize 请你给我一个C++的快排实现 -M
```

## 命令行模式
在终端中使用大模型的一大场景就是构造终端命令，在传统的交互逻辑中，我们需要从其他地方搜索、问答，然后再复制到终端中。baize 则提供了一种更优雅的方式，通过 `--cli -c` 打开，该参数下，模型会直接给出命令。如果你想要详细的命令解释，你可以使用 `--clidetail` 参数，该参数下，模型会给出详细的命令解释

```bash
baize -c 在 main.py 文件中找到字符串 name，并打印出行号
`grep -n 'name' main.py` 是否执行 [y/n]:
```

如果是在详细模式下，则会具体解释所给的命令

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

## 工具模式
工具模式基于 function call，使 baize 具有一定 Agent 能力，例如调用一些预定义的接口，如数学计算、Code Interpreter、天气查询等。使 baize 可以执行现实中的动作，帮助我们解决一些简单的实际问题。考虑到目前各家大模型 Agent 的能力差异较大，需要能力较强的大模型才能很好地执行工具模式

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

# weather 是天气查询工具，定义了获取当前日期和根据日期、地点查询天气的函数
baize --tool weather --log
> 查询今天上海的天气
正在调用 `get_current_date`

get_current_date()

2024-06-27
正在调用 `get_weather`

get_weather(city="""上海""",date="""2024-06-24""")

{'reason': '查询成功!', 'result': {'city': '上海', {'date': '2024-06-27', 'temperature': '23/25℃', 'weather': '中雨', 'wid': {'day': '08', 'night': '08'}, 'direct': '持续无风向'}, 'error_code': 0}}

根据查询结果，2024年6月27日上海的天气情况如下：温度为23/25℃，天气状况为中雨，风向为持续无风向。请注意，由于是中雨天气，建议您当天外出时准备好雨具。
```

## Prompt 构造

当 Prompt 模板中存在 `{}` 时，会按照输入数量进行格式化，例如：

```bash
# example: 我是{}，今年 {} 岁
# 匹配成：我是小明，今年 3 岁
baize 小明 3 -t example
```

如果正常文本中有 `{}`，请转义成 `{{}}`

对于没有 `{}` 的 Prompt 模板，会直接进行顺序拼接，例如：

```bash
# example: 翻译成中文
# 匹配成：翻译成英文 \n hello world
baize hello world -t example
```

### 设置上下文
Context 是一个对用户进行描述的系统 Prompt，你可以在这里定义你的背景信息和希望得到的回答是什么，可以更好地与大模型对齐，这个设置是全局生效的，之后每次调用大模型都会附带这个 Context

```bash
baize --setcontext 我是一个程序员
```

你可以通过 `--context` 查看当前所用的 Context；通过 `--resetcontext` 删除 Context

## 工作流模式
工作流能够自定义一个简单的大模型交互流程，通过 `--workflow -w` 来指定一个预定义的工作流执行。工作流是一个由节点定义的有向无环图的流程结构，其中节点包括「输入节点」、「LLM 节点」、「Python 脚本节点」、「输出节点」，通过将这些节点组合成一个流程来实现一些复杂任务的自动化

> 工作流的交互逻辑待优化，目前仅实现基本功能

```bash
baize -w example
请输入参数 prompt: 生成一首诗

秋风起，黄叶飘，
寂寥世界，诗意渺。
月挂梢头，霜满地，
独行人影，长桥倒。
```

示例的背后实际上定义了一个并行结构，对于输入的 `prompt`，会有两个「LLM 节点」同时生成一首诗，接着再有一个「LLM 节点」来判断哪一首诗更好，输出更好的那首诗

## 其他
你可以使用 `baize --help` 查看所有命令和选项
