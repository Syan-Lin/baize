import sys
import subprocess
from rich import print as rprint
from argparse import Namespace
from llm.base_llm import BaseLLM
from utils.render import print_markdown
from utils.resource import get_resource, ResourceType
from utils.context import print_messages


def remove_wrapper(message: str):
    message = message.strip()
    if message.startswith('```bash'):
        message = message.replace('```bash', '', 1)
        message = message[:-3]
    message = message.strip()
    lines = message.splitlines()
    if len(lines) > 1:
        rprint(f'[red]错误：返回包含多行输入，无法构建命令[/red]\n{message}')
        sys.exit()
    return message


def make_cli_prompt(args: Namespace) -> list[dict]:
    # Prompt 输入
    if not args.prompt and not args.paste:
        rprint('[red]错误：没有 Prpmpt 输入[/red]')
        sys.exit(1)
    input_prompt = []
    if args.paste:
        import pyperclip
        input_prompt = [pyperclip.paste()]
    if args.prompt:
        input_prompt = args.prompt + ['\n'] + input_prompt

    from utils.templates import expand_prompt
    messages = []
    template = get_resource(ResourceType.templates, 'cli_mode')
    template_format = template + '\n' + expand_prompt(input_prompt)
    user_message = {'role': 'user', 'content': template_format}
    messages.append(user_message)

    return messages


def make_cli_explain(args: Namespace, cli_command: str) -> list[dict]:
    messages = []
    template = get_resource(ResourceType.templates, 'cli_explain')
    template_format = template + '\n' + cli_command
    user_message = {'role': 'user', 'content': template_format}
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