import os
import sys
import subprocess
from rich import print as rprint
from argparse import Namespace
from llm.base_llm import BaseLLM
from utils.render import print_markdown
from utils.resource import get_resource, ResourceType
from utils.context import print_messages


SYSTEM_PROMPT = f'用户当前使用的是 {os.getenv('SHELL')}，请你基于当前 shell 进行命令生成和分析'


def remove_wrapper(message: str):
    message = message.strip()
    lines = message.splitlines()
    if len(lines) == 1:
        message = lines[0].strip()
    elif len(lines) == 3:
        message = lines[1].strip()
    else:
        rprint(f'[red]错误：返回包含多行输入，无法构建命令[/red]\n{message}')
        sys.exit()
    if message.startswith('`'):
        message = message[1:-1]
    return message


def make_cli_prompt(args: Namespace) -> list[dict]:
    # Prompt 输入
    from baize import make_formatter
    from utils.templates import format_template
    formatter = make_formatter(args)

    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    template = get_resource(ResourceType.templates, 'cli_mode')
    user_message = {'role': 'user', 'content': format_template(formatter, template)}
    messages.append(user_message)

    return messages


def make_cli_explain(args: Namespace, cli_command: str) -> list[dict]:
    from baize import make_formatter
    from utils.templates import format_template
    messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]
    template = get_resource(ResourceType.templates, 'cli_explain')
    user_message = {'role': 'user', 'content': format_template(make_formatter(args, prompt=cli_command), template)}
    messages.append(user_message)

    return messages


def cli_main(args: Namespace, llm: BaseLLM):
    messages = make_cli_prompt(args)
    resp = llm.message(messages)
    cli_command = remove_wrapper(resp)
    if args.clikey:
        print(cli_command)
        sys.exit()

    messages.append({'role': 'assistant', 'content': cli_command})

    stream = False
    if args.stream:
        stream = True

    buffer = ''
    if args.clidetail:
        messages_explain = make_cli_explain(args, cli_command)
        if stream:
            response = llm.stream_message(messages_explain)
            for block in response:
                buffer += block
                sys.stdout.write(block)
                sys.stdout.flush()
        else:
            response = llm.message(messages_explain)
            buffer += response
            if args.markdown:
                print_markdown(response)
            else:
                sys.stdout.write(response)
                sys.stdout.flush()
        messages.append({'role': 'assistant', 'content': buffer})
        print()

    if args.log:
        print_messages(messages)

    choice = ''
    while choice != 'y' and choice != 'n':
        choice = input(f'`{cli_command}` 是否执行 [y/n]: ')
    if choice == 'y':
        result = subprocess.run(cli_command, capture_output=True, text=True, shell=True, encoding='utf-8')
        if result.stderr:
            print(result.stderr)
        else:
            print(result.stdout)

        result_message = {'role': 'system', 'content': result.stdout}
        messages.append(result_message)

        # 历史对话保存
        from utils.context import save_previous
        save_previous(messages)