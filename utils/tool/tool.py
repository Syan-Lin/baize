import os
import sys
import json
from datetime import datetime
import subprocess
from rich import print as rprint
from argparse import Namespace
from llm.base_llm import BaseLLM
from utils.render import print_code, print_markdown
from utils.resource import get_resource, print_resource_table, get_resource_path, ResourceType
from utils.setup import input_param
from utils.log import log, logging


CODE_TEMPLATE = '''
{custom_code}
result = {function}({params})
print(result)
'''


def create_tool():
    import pyperclip
    rprint('准备开始创建工具，代码会自动从剪贴板获取，请确保 [green]剪贴板中已经复制[/green] 了代码，程序在输入任意键后开始...', end='')
    input()
    tool_code = pyperclip.paste()
    rprint('系统 Prompt 会自动从剪贴板获取，请确保 [green]剪贴板中已经复制[/green] 了系统 Prompt，程序在输入任意键后开始...', end='')
    input()
    sys_prompt = pyperclip.paste()
    tool_name = input_param('工具名称')
    tool_describe = input_param('工具描述', skip=True)
    author = input_param('作者', skip=True)
    python_path = input_param('Python 路径', skip=True)
    if python_path is None:
        python_path = 'python'
    date = datetime.now().strftime('%Y-%m-%d')

    rprint('\n[red]系统 Prompt[/red]:\n')
    print(sys_prompt)
    rprint('\n[blue]工具代码[/blue]:\n')
    print_code(tool_code, 'python')
    from utils.tool.signature import get_function_signatures
    try:
        signatures = get_function_signatures(tool_code)
    except Exception as e:
        rprint(f'[red]错误: 代码解析失败，请检查是否有语法错误！[/red]\n{e}')
        sys.exit()
    rprint('\n[blue]工具描述[/blue]:\n', json.dumps(signatures, ensure_ascii=False, indent=4))

    rprint('\n[blue]模板元信息[/blue]: ')

    tool_list = [{
        'name': tool_name,
        'describe': tool_describe,
        'author': author,
        'date': date,
    }]

    print_resource_table(tool_list)

    choice = ''
    while choice != 'y' and choice != 'n':
        print('确认保存 [y/n]: ', end='')
        choice = input()

    if choice == 'y':
        tool_root_path = get_resource_path(ResourceType.tool)
        new_tool_path = os.path.join(tool_root_path, tool_name)
        if os.path.exists(new_tool_path):
            rprint('[red]错误: 工具已存在，无法创建！[/red]')
            return
        os.makedirs(new_tool_path)
        with open(os.path.join(new_tool_path, 'meta.json'), 'w', encoding='utf-8') as f:
            json.dump({
                'describe': tool_describe,
                'author': author,
                'date': date,
            }, f, ensure_ascii=False)
        with open(os.path.join(new_tool_path, 'tool.py'), 'w', encoding='utf-8') as f:
            f.write(tool_code)
        with open(os.path.join(new_tool_path, 'sys.md'), 'w', encoding='utf-8') as f:
            f.write(sys_prompt)
        with open(os.path.join(new_tool_path,'tool.json'), 'w', encoding='utf-8') as f:
            tool_config = {
                'python': python_path,
                'tools': signatures
            }
            json.dump(tool_config, f, ensure_ascii=False)
        info = f'工具创建成功！保存在目录 {new_tool_path}'
        rprint('[green]' + info + '[/green]')


@log
def get_input() -> str:
    print('> ', end='')
    prompt = input()
    if prompt.lower() == '/q':
        sys.exit()
    import pyperclip
    prompt = prompt.replace('/p', pyperclip.paste())
    return prompt


@log
def make_call(params: dict) -> str:
    params = json.loads(params)
    params_str = ''
    for param, value in params.items():
        params_str += f'{param}="""{value}""",'
    params_str = params_str.rstrip(',')
    return params_str


@log
def call(python: str, custom_code: str, function: str, params_str: str, log: bool) -> str:
    rprint(f'[blue]正在调用[/blue] [green]`{function}`[/green]')
    exec_code = CODE_TEMPLATE.format(custom_code=custom_code, function=function, params=params_str)
    result = subprocess.run([python, "-c", exec_code], capture_output=True, text=True)

    if log:
        if result.stdout:
            print_markdown(f'输出: {result.stdout}')
        if result.stderr:
            print_markdown(f'错误: {result.stderr}')

    if result.stderr:
        script_output = result.stderr
    else:
        script_output = result.stdout
    return script_output


def tool_main(args: Namespace, llm: BaseLLM):
    # 读取 tools 配置和脚本文件
    config = get_resource(ResourceType.tool, args.tool[0])
    config = json.loads(config)
    tools = config['tools']
    python = config['python']
    script_path = os.path.join(get_resource_path(ResourceType.tool), args.tool[0], 'tool.py')
    sys_prompt_path = os.path.join(get_resource_path(ResourceType.tool), args.tool[0], 'sys.md')
    if not os.path.exists(sys_prompt_path):
        rprint(f'[red]错误: 工具 {args.tool[0]} 的系统 Prompt 不存在[/red]')
        sys.exit()
    with open(sys_prompt_path, "r", encoding="utf-8") as f:
        sys_prompt = f.read()

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            custom_code = f.read()
    except Exception as e:
        raise ValueError(f'读取脚本文件 {script_path} 失败: {e}')

    # function call
    messages = [{'role': 'system', 'content': sys_prompt}]

    rprint('[green]（工具模式中输入 `/q` 退出）[/green]')
    while True:
        user_message = {'role': 'user', 'content': get_input()}
        messages.append(user_message)

        while True:
            response, function, params, tool_message = llm.call_tool(tools, messages)
            make_function_call = function is not None and params is not None and tool_message is not None
            if not make_function_call:
                break
            messages.append(tool_message)
            params_str = make_call(params)

            print_markdown(f'```python\n{'{function}({params})'.format(function=function, params=params_str)}\n```')

            messages.append({
                "role": "tool",
                "content": call(python, custom_code, function, params_str, args.log),
                "tool_call_id": tool_message['tool_calls'][0]['id']
            })
        logging.info(response)
        rprint(f'[green]{response}[/green]')
        messages.append({'role': 'assistant', 'content': response})