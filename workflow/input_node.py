import sys
from workflow.node import Node
from rich import print as rprint


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
                    rprint(f'节点 [green]{self.name}[/green] 中，命令 [green]`{self.command}`[/green] 执行错误:\n {result.stderr}')
                    sys.exit()
            else:
                raise ValueError(f'节点 [green]{self.name}[/green] 中，输入参数 [green]{param_name}[/green] 格式错误')

        self.debug_output(param)
        return param
