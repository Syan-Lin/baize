from workflow.node import Node
from utils.config import model_config
from baize import get_llm
from rich import print as rprint

class LLMNode(Node):
    '''大语言执行 Node, 用于调用 LLM, 其输入是其他节点的输出'''
    def __init__(self, name: str, config_name: str, template: str = '', content: str = '', output_param: str = ''):
        super().__init__(name, 'llm')

        config = model_config()
        if config_name not in list(config.keys()):
            raise ValueError(f'节点 {self.name} 未找到配置 {config_name}')
        self.llm = get_llm(config[config_name]['model_name'], config[config_name])

        if template == '' and content == '':
            raise ValueError(f'节点 {self.name} 至少需要 template 或 content 参数')
        self.template = template
        self.content = content
        self.output_param = output_param
        self.input = []


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
            from utils.templates import get_template
            prompt += get_template(self.template) + '\n'
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