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
        self.config = {
            'type': type,
            'input': []
        }


    @abstractmethod
    def output(self) -> dict:
        raise NotImplementedError

    def add_input(self, node):
        if node not in self.input:
            self.input.append(node)
            self.config['input'].append(node.name)


    def remove_input(self, node):
        if node in self.input:
            self.input.remove(node)
            self.config['input'].remove(node.name)


    def enable_debug(self):
        self.debug = True


    def debug_output(self, output: dict):
        if self.debug:
            rprint(f'节点 [green]{self.name}[/green] 输出: {output}')


class EmptyNode(Node):
    def __init__(self, name: str):
        super().__init__(name, "empty")
    def output(self) -> dict:
        raise NotImplementedError


def make_input_node(name: str, config: dict) -> Node:
    return InputNode(name, config['output'])


class InputNode(Node):
    '''输入 Node, 用于接收用户输入, 其输入只能是字符串或命令'''
    def __init__(self, name: str, input_dict: dict):
        super().__init__(name, "input")
        self.input_dict = input_dict
        self.param = {}

        self.config['output'] = input_dict


    def output(self) -> dict:
        if len(self.param) > 0:
            return self.param

        for param_name, value in self.input_dict.items():
            if self.debug and 'command' in value:
                rprint(f'节点 [green]{self.name}[/green] 执行命令: [red]{value['command']}[/red]')

            if 'content' in value:
                self.param[param_name] = value['content']
            elif 'command' in value:
                import subprocess
                result = subprocess.run(value['command'], capture_output=True, text=True, shell=True, encoding='utf-8')
                if result.stdout:
                    self.param[param_name] = result.stdout
                if result.stderr:
                    rprint(f'[red]错误: 节点 {self.name} 中，命令 [/red][green]`{self.command}`[/green] [red]执行错误:\n {result.stderr}[/red]')
                    sys.exit()
            else:
                rprint(f'请输入参数[green] {param_name} [/green]: ')
                in_loop = True
                param_content = ''
                while in_loop:
                   user_input = input()
                   if not user_input.endswith('\\'):
                       in_loop = False
                   param_content += user_input[:-1] + '\n'
                self.param[param_name] = param_content

        self.debug_output(self.param)
        return self.param


def make_llm_node(name: str, config: dict) -> Node:
    if 'config' not in config:
        from utils.config import model_config
        configs_info = model_config()
        if 'default_config' not in configs_info.keys():
            rprint('[red]错误: 请先运行 `baize --setup` 配置模型[/red]')
            sys.exit()
        config_name = configs_info['default_config']
    else:
        config_name = config['config']

    template, content, system = '', '', ''
    if 'template' in config:
        template = config['template']
    if 'content' in config:
        content = config['content']
    if 'system' in config:
        system = config['system']
    if template == '' and content == '':
        rprint(f'[red]错误: 节点 {name} 至少需要 template 或 content 参数[/red]')
        sys.exit()

    if 'output' not in config:
        rprint(f'[red]错误: 节点 {name} 缺少 output 参数！[/red]')
        sys.exit()

    output = config['output']
    return LLMNode(name, config_name, template, content, output, system)


class LLMNode(Node):
    '''大语言执行 Node, 用于调用 LLM, 其输入是其他节点的输出'''
    def __init__(self, name: str, config_name: str, template: str = '', content: str = '', output_param: str = '', system_prompt: str = ''):
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
        self.system_prompt = system_prompt
        self.response = {}

        self.config['system'] = system_prompt
        self.config['template'] = template
        self.config['content'] = content
        self.config['output'] = output_param


    def output(self) -> dict:
        if len(self.response) > 0:
            return self.response
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
        if self.system_prompt != '':
            messages.append({'role': 'system', 'content': self.system_prompt})
        messages.append({'role': 'user', 'content': prompt_format})
        result = self.llm.message(messages)
        if self.output_param != '':
            self.response = {self.output_param: result}
        else:
            self.response = {'output': result}

        self.debug_output(self.response)
        return self.response


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

        self.config['to'] = to


    def output(self) -> dict:
        if len(self.input) == 0:
            raise ValueError(f'节点 {self.name} 没有输入')

        output = {}
        for inp in self.input:
            output.update(inp.output())

        output_text = '\n'
        for key, value in output.items():
            output_text += f'{key}:\n{value}\n\n'

        self.debug_output(output)

        if self.to == 'console':
            rprint(f'[green]{output_text}[/green]', end='')
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

        self.config['script'] = script_path
        self.config['function'] = function
        self.config['output'] = output_param


    def generate_code(self) -> str:
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                custom_code = f.read()
        except Exception as e:
            raise ValueError(f'读取脚本文件 {self.script_path} 失败: {e}')

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