from workflow.node import Node


class OutputNode(Node):
    def __init__(self, name: str, to: str):
        super().__init__(name, 'output')

        self.to = to
        self.input = []


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

        if self.to == 'console':
            print(output_text, end='')
        else:
            with open(self.to, 'w', encoding='utf-8') as f:
                f.write(output_text)

        self.debug_output(output)
        return output