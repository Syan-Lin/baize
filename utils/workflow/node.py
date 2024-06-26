import os
import sys
import json
import subprocess
from abc import ABC, abstractmethod
from rich import print as rprint
from utils.resource import get_resource, ResourceType


class Node(ABC):
    '''Node 表达有向无环图中的一个节点'''
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type
        self.debug = False
        self.input = []


    @abstractmethod
    def output(self) -> dict:
        raise NotImplementedError


    def enable_debug(self):
        self.debug = True


    def debug_output(self, output: dict):
        if self.debug:
            rprint(f'节点 [green]{self.name}[/green] 输出: {output}')


def make_input_node(name: str, config: dict) -> Node:
    return InputNode(name, config['output'])


class InputNode(Node):
    '''输入 Node, 用于接收用户输入, 其输入只能是字符串或命令'''
    def __init__(self, name: str, input_dict: dict):
        super().__init__(name, "input")
        self.input_dict = input_dict


    def output(self) -> dict:
        param = {}
        for param_name, value in self.input_dict.items():

            if self.debug and 'command' in value:
                rprint(f'节点 [green]{self.name}[/green] 执行命令: [red]{value['command']}[/red]')

            if 'content' in value:
                param[param_name] = value['content']
            elif 'command' in value:
                import subprocess
                result = subprocess.run(value['command'], capture_output=True, text=True, shell=True, encoding='utf-8')
                if result.stdout:
                    param[param_name] = result.stdout
                if result.stderr:
                    rprint(f'[red]错误: 节点 {self.name} 中，命令 [/red][green]`{self.command}`[/green] [red]执行错误:\n {result.stderr}[/red]')
                    sys.exit()
            else:
                rprint(f'请输入参数[green] {param_name} [/green]: ')
                param[param_name] = input()

        self.debug_output(param)
        return param


def make_llm_node(name: str, config: dict) -> Node:
    if 'model' not in config:
        rprint(f'[red]错误: 节点 {name} 缺少 model 参数！[/red]')
        sys.exit()
    model = config['model']

    template, content = '', ''
    if 'template' in config:
        template = config['template']
    if 'content' in config:
        content = config['content']
    if template == '' and content == '':
        rprint(f'[red]错误: 节点 {name} 至少需要 template 或 content 参数[/red]')
        sys.exit()

    if 'output' not in config:
        rprint(f'[red]错误: 节点 {name} 缺少 output 参数！[/red]')
        sys.exit()

    output = config['output']
    return LLMNode(name, model, template, content, output)


class LLMNode(Node):
    '''大语言执行 Node, 用于调用 LLM, 其输入是其他节点的输出'''
    def __init__(self, name: str, config_name: str, template: str = '', content: str = '', output_param: str = ''):
        super().__init__(name, 'llm')

        from utils.config import model_config
        from baize import get_llm
        config = model_config()
        if config_name not in list(config.keys()):
            raise ValueError(f'节点 {self.name} 未找到配置 {config_name}')
        self.llm = get_llm(config[config_name]['model_name'], config[config_name])

        if template == '' and content == '':
            raise ValueError(f'节点 {self.name} 至少需要 template 或 content 参数')
        self.template = template
        self.content = content
        self.output_param = output_param


    def add_input(self, input: Node):
        self.input.append(input)


    def output(self) -> dict:
        if len(self.input) == 0:
            raise ValueError(f'节点 {self.name} 没有输入')

        input_params = {}
        for inp in self.input:
            inp_output = inp.output()
            input_params.update(inp_output)

        prompt = ''
        if self.template != '':
            prompt += get_resource(ResourceType.templates, self.template) + '\n'
        if self.content != '':
            prompt += self.content
        if prompt == '':
            raise ValueError(f'节点 {self.name} 没有 Prompt')

        format_num = prompt.count('{}')
        if format_num == 0:
            params = ''
            for _, value in input_params.items():
                params += str(value) + ' '
            prompt_format = prompt + '\n' + params
        else:
            if len(input_params) != format_num:
                raise ValueError(f'节点 {self.name} 输入参数数量与模板不一致(param: {len(input_params)}, template: {format_num}) ')
            params = []
            for _, value in input_params.items():
                params.append(str(value))
            prompt_format = prompt.format(*params)

        if self.debug:
            rprint(f'节点 [green]{self.name}[/green] prompt:\n[blue]{prompt_format}[/blue]')

        messages = []
        messages.append({'role': 'user', 'content': prompt_format})
        result = self.llm.message(messages)
        if self.output_param != '':
            output = {self.output_param: result}
        else:
            output = {'output': result}

        self.debug_output(output)
        return output


def make_output_node(name: str, config: dict) -> Node:
    if 'to' not in config:
        rprint(f'[red]错误: 节点 {name} 缺少 to 参数！[/red]')
        sys.exit()
    to = config['to']

    return OutputNode(name, to)


class OutputNode(Node):
    def __init__(self, name: str, to: str):
        super().__init__(name, 'output')
        self.to = to


    def add_input(self, input: Node):
        self.input.append(input)


    def output(self) -> dict:
        if len(self.input) == 0:
            raise ValueError(f'节点 {self.name} 没有输入')

        output = {}
        for inp in self.input:
            output.update(inp.output())

        output_text = ''
        for key, value in output.items():
            output_text += f'{key}:\n{value}\n\n'

        self.debug_output(output)

        if self.to == 'console':
            print(output_text, end='')
        else:
            with open(self.to, 'w', encoding='utf-8') as f:
                f.write(output_text)
            print(f'输出到文件 {os.path.abspath(self.to)}')

        return output


def make_script_node(name: str, config: dict) -> Node:
    if 'script' not in config:
        rprint(f'[red]错误: 节点 {name} 缺少 script 路径参数！[/red]')
        sys.exit()
    script_path = config['script']

    if 'function' not in config:
        rprint(f'[red]错误: 节点 {name} 缺少 function 参数！[/red]')
        sys.exit()
    function = config['function']

    python_path = 'python'
    if 'python' in config:
        python_path = config['python']

    if 'output' in config:
        output = config['output']

    return ScriptNode(name, script_path, function, output, python_path)


CODE_TEMPLATE = '''
import json
{custom_code}
result = {function}({params})
print(json.dumps(result))
'''

class ScriptNode(Node):
    '''脚本执行 Node'''
    def __init__(self, name: str, script_path: str, function: str, output_param: list | str, python_path: str):
        super().__init__(name, 'script')

        if isinstance(output_param, str):
            output_param = [output_param]
        self.output_param = output_param
        self.python_path = python_path
        if '~' in script_path:
            self.script_path = os.path.expanduser(script_path)
        else:
            self.script_path = script_path
        self.function = function


    def add_input(self, input: Node):
        self.input.append(input)


    def generate_code(self) -> str:
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                custom_code = f.read()
        except Exception as e:
            raise ValueError(f'读取脚本文件 {self.script_path} 失败')

        input_params = {}
        for inp in self.input:
            input_params.update(inp.output())
        params = ''
        for param, value in input_params.items():
            params += f'{param}="""{value}""",'
        params = params.rstrip(',')

        exec_code = CODE_TEMPLATE.format(custom_code=custom_code, function=self.function, params=params)
        return exec_code


    def output(self) -> dict:
        if len(self.input) == 0:
            raise ValueError(f'节点 {self.name} 没有输入')

        script = self.generate_code()

        if self.debug:
            rprint(f'节点 [green]{self.name}[/green] python_path: {self.python_path}')
            rprint(f'节点 [green]{self.name}[/green] 执行脚本:\n[yellow]{script}[/yellow]')

        result = subprocess.run([self.python_path, "-c", script], capture_output=True, text=True)
        if result.stderr:
            raise ValueError(f'节点 {self.name} 执行失败: {result.stderr}')
        script_output = result.stdout

        script_output = json.loads(script_output)

        output = {}
        for param in self.output_param:
            if param not in script_output:
                raise ValueError(f'节点 {self.name} 输出参数 {param} 不存在')
            else:
                output[param] = script_output[param]

        self.debug_output(output)
        return output


class InterpreterNode(Node):
    def __init__(self, name: str, python_path: str = ''):
        super().__init__(name, 'interpreter')