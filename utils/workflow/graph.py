import sys
import json
from rich import print as rprint
from utils.workflow.node import (
    Node,
    OutputNode,
    make_input_node,
    make_llm_node,
    make_output_node,
    make_script_node
)


def init_graph(workflow_config: dict, debug: bool):
    graph = Graph()
    nodes = {}
    for name, config in workflow_config.items():
        if config['type'] == 'input':
            node = make_input_node(name, config)
        elif config['type'] == 'llm':
            node = make_llm_node(name, config)
        elif config['type'] == 'script':
            node = make_script_node(name, config)
        elif config['type'] == 'output':
            node = make_output_node(name, config)
        else:
            rprint(f'[red]错误: 节点 {name} 类型错误，不存在类型 {config['type']}[/red]')
            sys.exit()
        if debug:
            node.enable_debug()
        graph.add_node(node)
        nodes[name] = node

    for name, config in workflow_config.items():
        if 'input' not in config:
            continue
        for input_node in config['input']:
            if input_node not in nodes:
                rprint(f'[red]错误: 节点 {name} 的输入节点 [red]{input_node}[/red] 不存在！[/red]')
                sys.exit()
            nodes[name].add_input(nodes[input_node])

    graph.check_loop()

    return graph


class Graph:
    def __init__(self):
        self.nodes = []
        self.output_node = None


    def add_node(self, node: Node):
        if node in self.nodes:
            rprint(f'[red]错误: 节点 {node.name} 已经存在！[/red]')
            sys.exit()
        if isinstance(node, OutputNode):
            if self.output_node is not None:
               rprint(f'[red]错误: 只能存在一个输出节点，节点 {node.name} 产生重复！[/red]')
               sys.exit()
            self.output_node = node

        self.nodes.append(node)


    def check_loop(self):
        states = {}
        for node in self.nodes:
            states[node] = 0
        loop_node = None

        def dfs(node: Node):
            nonlocal loop_node
            if loop_node is not None or states[node] == 2:
                return
            if states[node] == 1:
                loop_node = node
                return
            states[node] = 1
            for next_node in node.input:
                dfs(next_node)
            states[node] = 2

        for node in self.nodes:
            if states[node] == 0:
                dfs(node)

        if loop_node is not None:
            rprint(f'[red]错误: Workflow 存在环，出现在节点 {loop_node.name}[/red]')
            sys.exit()


    def run(self):
        if self.output_node is None:
            rprint('[red]错误: Workflow 没有输出节点[/red]')
            sys.exit()
        return self.output_node.output()