from abc import ABC, abstractmethod
from rich import print as rprint


class Node(ABC):
    '''Node 表达有向无环图中的一个节点'''
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type
        self.debug = False


    @abstractmethod
    def output(self) -> dict:
        raise NotImplementedError


    def enable_debug(self):
        self.debug = True


    def debug_output(self, output: dict):
        if self.debug:
            rprint(f'节点 [green]{self.name}[/green] 输出: {output}')