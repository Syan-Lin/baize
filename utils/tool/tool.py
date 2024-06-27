import os
import sys
import json
import subprocess
from rich import print as rprint
from argparse import Namespace
from llm.base_llm import BaseLLM
from utils.render import print_markdown
from utils.resource import get_resource, get_resource_path, ResourceType

SYSTEM_PROMPT = '''
# OBJECTIVE
你是一个 Agent 助手，你会根据用户的请求构造调用函数的参数，并调用函数，最后基于函数的返回值给出相应的响应。

如果用户没有提供足够的信息来调用函数，请继续提问以确保收集到了足够的信息。
在调用函数之前，你必须总结用户的描述并向用户提供总结，询问他们是否需要进行任何修改。

请你深呼吸，保持专注，按照以下要求逐点检查：
1. 你需要逐一检查函数调用的所有必须参数，用户是否提供了足够的信息来构造函数调用所需的所有参数；如果没有，你需要询问用户相对应的参数信息，并等待用户回复。
2. 不要捏造参数字段，如果用户没有提供这些参数，必须询问用户并等待用户回复。
'''

CODE_TEMPLATE = '''
{custom_code}
result = {function}({params})
print(result)
'''


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
    messages.append({
        "role": "system",
        "content": SYSTEM_PROMPT
    })

    while True:
        print('> ', end='')
        prompt = input()
        if prompt.lower() == 'exit' or prompt.lower() == 'q':
            sys.exit()
        user_message = {'role': 'user', 'content': prompt}
        messages.append(user_message)

        while True:
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

            rprint(f'[blue]正在调用[/blue] [green]`{function}`[/green]')
            exec_code = CODE_TEMPLATE.format(custom_code=custom_code, function=function, params=params_str)
            result = subprocess.run([python, "-c", exec_code], capture_output=True, text=True)

            if args.log:
                from utils.render import print_code, print_markdown
                print_markdown(f'```python\n{'{function}({params})'.format(function=function, params=params_str)}\n```')
                if result.stderr:
                    print_markdown(f'{result.stderr}')
                else:
                    print_markdown(f'{result.stdout}')

            if result.stderr:
                script_output = result.stderr
            else:
                script_output = result.stdout

            messages.append({
                "role": "tool",
                "content": script_output,
                "tool_call_id": tool_message['tool_calls'][0]['id']
            })

        rprint(f'[green]{response}[/green]')
        messages.append({'role': 'assistant', 'content': response})