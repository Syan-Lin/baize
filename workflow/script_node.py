import json
import subprocess
from workflow.node import Node
from rich import print as rprint

code = '''
import json
{custom_code}
result = {function}({params})
print(json.dumps(result))
'''

class ScriptNode(Node):
    '''脚本执行 Node'''
    def __init__(self, name: str, python_path: str, script_path: str, function: str, output_param: list | str):
        super().__init__(name, 'script')

        if isinstance(output_param, str):
            output_param = [output_param]
        self.output_param = output_param
        self.python_path = python_path
        self.script_path = script_path
        self.function = function
        self.input = []


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
            params += f'{param}="{value}",'
        params = params.rstrip(',')

        exec_code = code.format(custom_code=custom_code, function=self.function, params=params)
        return exec_code


    def output(self) -> dict:
        if len(self.input) == 0:
            raise ValueError(f'节点 {self.name} 没有输入')

        script = self.generate_code()

        if self.debug:
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