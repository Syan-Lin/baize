import os
import sys
import json
import subprocess
from rich import print as rprint
from argparse import Namespace
from llm.base_llm import BaseLLM
from utils.render import print_markdown
from utils.resource import get_resource, get_resource_path, ResourceType

CODE_TEMPLATE = '''
{custom_code}
result = {function}({params})
print(result)
'''

MAX_RETRY = 3


def tool_main(args: Namespace, llm: BaseLLM):
    # 读取 tools 配置和脚本文件
    config = get_resource(ResourceType.tool, args.tool[0])
    config = json.loads(config)
    tools = config['tools']
    python = config['python']
    script_path = os.path.join(get_resource_path(ResourceType.tool), args.tool[0], 'tool.py')

    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            custom_code = f.read()
    except Exception as e:
        raise ValueError(f'读取脚本文件 {script_path} 失败: {e}')

    # function call
    messages = []
    retry = 0

    while True:
        print('> ', end='')
        prompt = input()
        user_message = {'role': 'user', 'content': prompt}
        messages.append(user_message)

        while retry < MAX_RETRY:
            response, function, params, tool_message = llm.call_tool(tools, messages)
            make_function_call = function is not None and params is not None and tool_message is not None
            if not make_function_call:
                break

            # 构造调用
            messages.append(tool_message)
            params = json.loads(params)
            params_str = ''
            for param, value in params.items():
                params_str += f'{param}="""{value}""",'
            params_str = params_str.rstrip(',')

            exec_code = CODE_TEMPLATE.format(custom_code=custom_code, function=function, params=params_str)
            result = subprocess.run([python, "-c", exec_code], capture_output=True, text=True)

            if args.log:
                rprint(f'\ncode:[red]{exec_code}[/red]')
                rprint(f'output:\n[yellow]{result.stdout}[/yellow]')

            if result.stderr:
                messages.append({
                    "role": "tool",
                    "content": f'调用出现错误，请你重新调用：\n{result.stderr}',
                    "tool_call_id": tool_message['tool_calls'][0]['id']
                })
                retry += 1
                continue
            else:
                script_output = result.stdout

            messages.append({
                "role": "tool",
                "content": script_output,
                "tool_call_id": tool_message['tool_calls'][0]['id']
            })

            result = llm.message(messages)
            rprint(f'[green]{result}[/green]')
            sys.exit()

        if retry == MAX_RETRY:
            rprint(f'[red]调用工具失败，请重新尝试[/red]')
            sys.exit()
        rprint(f'[green]{response}[/green]')
        messages.append({'role': 'assistant', 'content': response})