import sys
from rich import print as rprint
from utils.log import log
from utils.workflow.node import (
    Node,
    OutputNode,
    make_input_node,
    make_llm_node,
    make_output_node,
    make_script_node
)


class Graph:
    def __init__(self):
        self.nodes = []
        self.output_node = None


    @log
    def edge(self, from_node_name: str, to_node_name: str):
        from_node = self.get_node(from_node_name)
        to_node = self.get_node(to_node_name)
        if from_node is None or to_node is None:
            return
        to_node.add_input(from_node)


    @log
    def remove_edge(self, from_node_name: str, to_node_name: str):
        from_node = self.get_node(from_node_name)
        to_node = self.get_node(to_node_name)
        if from_node is None or to_node is None:
            return
        to_node.remove_input(from_node)


    @log
    def add_node(self, node: Node):
        for n in self.nodes:
            if n.name == node.name:
                rprint(f'[red]错误: 节点 {node.name} 已经存在！[/red]')
                return
        if isinstance(node, OutputNode):
            if self.output_node is not None:
               rprint(f'[red]错误: 只能存在一个输出节点，节点 {node.name} 产生重复！[/red]')
               return
            self.output_node = node

        self.nodes.append(node)


    @log
    def get_node(self, name: str) -> Node:
        for node in self.nodes:
            if node.name == name:
                return node
        rprint(f'[red]错误: 节点 {name} 不存在！[/red]')
        return None


    @log
    def remove_node(self, name: str):
        dnode = None
        for node in self.nodes:
            if node.name == name:
                dnode = node
                break
        if dnode is None:
            return

        if dnode in self.nodes:
            self.nodes.remove(dnode)
            for node in self.nodes:
                node.remove_input(dnode)


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


def graph2ascii(graph: Graph):
    import networkx as nx
    from asciinet import graph_to_ascii
    graph_vis = nx.Graph()
    edges = []
    for node in graph.nodes:
        graph_vis.add_node(node.name)
        for inp in node.input:
            edges.append((node.name, inp.name))
    graph_vis.add_edges_from(edges)
    ascii = graph_to_ascii(graph_vis)
    return ascii


def print_graph(graph: Graph):
    ascii = graph2ascii(graph)
    print(ascii)


@log
def init_graph(workflow_config: dict, debug: bool):
    graph = Graph()
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

    for name, config in workflow_config.items():
        if 'input' not in config:
            continue
        for input_node in config['input']:
            if graph.get_node(input_node) is None:
                rprint(f'[red]错误: 节点 {name} 的输入节点 [red]{input_node}[/red] 不存在！[/red]')
                sys.exit()
            graph.edge(input_node, name)

    graph.check_loop()

    return graph


@log
def graph2config(graph: Graph) -> dict:
    config = {}
    graph.remove_node('root')
    for node in graph.nodes:
        config[node.name] = node.config
    return config