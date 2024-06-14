import argparse

def init_parse():
    parser = argparse.ArgumentParser(description='Baize: 将 LLM 集成至你的命令行！')

    parser.add_argument("prompt", nargs="?", type=str, help="命令行 Prompt")

    # 模型参数
    parser.add_argument('-s', '--stream', action='store_true', help='流式输出模式')
    parser.add_argument('-m', '--model', nargs=1, metavar='<model name>', type=str, help='设置模型')
    parser.add_argument('-t', '--templates', nargs=1, metavar='<template name>', type=str, help='Prompt 模板')
    parser.add_argument('-f', '--file', nargs="*", metavar='<file path>', type=str, help='上传文件')
    parser.add_argument('--set', nargs=1, metavar='<model name>', help='设置当前模型')

    # 配置
    parser.add_argument('--setup', action='store_true', help='配置新模型')
    parser.add_argument('--modellist', action='store_true', help='查看现有模型列表')
    parser.add_argument('-l', '--list', action='store_true', help='查看现有 Prompt 模板列表')
    parser.add_argument('--context', action='store_true', help='查看 Context Prompt')
    parser.add_argument('--setcontext', nargs=1, metavar='Context Prompt', type=str, help='设置 Context Prompt')

    # 执行模式
    parser.add_argument('--log', action='store_true', help='调试模式')
    parser.add_argument('-c', '--cli', metavar='<prompt>', type=str, help='命令行模式')
    parser.add_argument('--clidetail', metavar='<prompt>', type=str, help='命令行详细模式')
    parser.add_argument('-w', '--wrokflow', metavar='<workflow name>', help='设置工作流')

    # 输入输出
    parser.add_argument('-C', '--copy', action='store_true', help='输出复制到剪贴板')
    parser.add_argument('-P', '--paste', action='store_true', help='剪贴板作为输入')
    parser.add_argument('-o', '--output', metavar='<file path>', help='输出到文件')
    parser.add_argument('-v', '--voice', action='store_true', help='语音输出')

    args = parser.parse_args()

    return args