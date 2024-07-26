# Warning: pexpect 不支持 Windows 平台

import os
import sys
import time
import pexpect
import pyperclip
import argparse
from rich import print as rprint
from rich.markdown import Markdown
from rich.console import Console

console = Console()
split_line = Markdown('---')

def get_path():
    script_path = os.path.abspath(__file__)
    parent_directory = os.path.dirname(script_path)
    python_path = sys.executable
    baize_path = os.path.join(parent_directory, 'baize.py')

    return python_path, baize_path

python_path, baize_path = get_path()
debug = False


def has_error(stdout: str) -> bool:
    if 'Traceback (most recent call last)' in stdout\
        or 'Errno' in stdout or '错误' in stdout or 'Error' in stdout:
        return True
    return False


def check(chat, test_name: str, expect_error: bool = False):
    chat.expect(pexpect.EOF)
    stdout = chat.before.decode('utf-8')

    if debug:
        console.print(split_line)
    print(f'{test_name}: ', end='')
    if (has_error(stdout) and not expect_error) or (not has_error(stdout) and expect_error):
        rprint(f'[red]测试失败[/red]:\n{stdout}')
    else:
        rprint('[green]Check![/green]')
    if debug:
        print(f'{test_name} debug:\n{stdout}')


def test_settings():
    console.print(Markdown('# Setting Test'))

    # setup
    chat = pexpect.spawn(f'{python_path} {baize_path} --setup')
    chat.expect(':')
    chat.sendline('1')
    chat.expect(':')
    chat.sendline('test_setting')
    chat.expect(':')
    chat.sendline('1')
    chat.expect(':')
    chat.sendline()
    chat.expect(':')
    chat.sendline('apikey')
    chat.expect(':')
    chat.sendline()
    chat.expect(':')
    chat.sendline()
    chat.expect(':')
    chat.sendline()
    chat.expect(':')
    chat.sendline()
    chat.expect(':')
    chat.sendline('y')
    check(chat, 'setup')

    # modellist
    chat = pexpect.spawn(f'{python_path} {baize_path} --modellist')
    check(chat, 'modellist')

    # workflowlist
    chat = pexpect.spawn(f'{python_path} {baize_path} --workflowlist')
    check(chat, 'workflowlist')

    # set
    chat = pexpect.spawn(f'{python_path} {baize_path} --set test_setting')
    check(chat, 'set')

    # list
    chat = pexpect.spawn(f'{python_path} {baize_path} --list')
    check(chat, 'list')

    # context
    chat = pexpect.spawn(f'{python_path} {baize_path} --context')
    check(chat, 'context')

    # setcontext
    chat = pexpect.spawn(f'{python_path} {baize_path} --setcontext hhhh')
    check(chat, 'setcontext')
    chat = pexpect.spawn(f'{python_path} {baize_path} --context')
    check(chat, 'setcontext2')

    # resetcontext
    chat = pexpect.spawn(f'{python_path} {baize_path} --resetcontext')
    check(chat, 'resetcontext')
    chat = pexpect.spawn(f'{python_path} {baize_path} --context')
    check(chat, 'resetcontext2')

    # createtemplate
    pyperclip.copy('你好')
    chat = pexpect.spawn(f'{python_path} {baize_path} --createtemplate')
    chat.expect('.')
    chat.sendline()
    chat.expect(':')
    chat.sendline('test_setting')
    chat.expect(':')
    chat.sendline('test_setting')
    chat.expect(':')
    chat.sendline('test_setting')
    chat.expect(':')
    chat.sendline('y')
    check(chat, 'createtemplate')
    chat = pexpect.spawn(f'{python_path} {baize_path} --list')
    check(chat, 'createtemplate2')

    # deletetemplate
    chat = pexpect.spawn(f'{python_path} {baize_path} --deletetemplate test_setting')
    chat.expect(':')
    chat.sendline('y')
    check(chat, 'deletetemplate')
    chat = pexpect.spawn(f'{python_path} {baize_path} --list')
    check(chat, 'deletetemplate2')

    # showtemplate
    chat = pexpect.spawn(f'{python_path} {baize_path} --showtemplate cli_mode')
    check(chat, 'showtemplate')

    # init
    chat = pexpect.spawn(f'{python_path} {baize_path} --init zsh')
    check(chat, 'init1')
    chat = pexpect.spawn(f'{python_path} {baize_path} --init bash')
    check(chat, 'init2')

    # version
    chat = pexpect.spawn(f'{python_path} {baize_path} --version')
    check(chat, 'version')

    # deletemodel
    chat = pexpect.spawn(f'{python_path} {baize_path} --deletemodel test_setting')
    chat.expect(':')
    chat.sendline('y')
    check(chat, 'deletemodel')


def test_input():
    console.print(Markdown('# Input Test'))

    # 基础 prompt
    chat = pexpect.spawn(f'{python_path} {baize_path} 你好')
    check(chat, '基础 prompt')

    # 多段 prompt
    chat = pexpect.spawn(f'{python_path} {baize_path} 你好 我是小明 今年 3 岁')
    check(chat, '多段 prompt')

    # paste
    pyperclip.copy('hello')
    chat = pexpect.spawn(f'{python_path} {baize_path} -P')
    check(chat, 'paste')

    # sysin
    chat = pexpect.spawn(f'/bin/bash -c "echo nihao | {python_path} {baize_path}"')
    check(chat, 'sysin')

    # paste + prompt
    pyperclip.copy('我是小明')
    chat = pexpect.spawn(f'{python_path} {baize_path} -P 你好 我叫什么。')
    check(chat, 'paste + prompt')

    # sysin + prompt
    chat = pexpect.spawn(f'/bin/bash -c "echo 我是小明 | {python_path} {baize_path} 你好 我叫什么。"')
    check(chat, 'sysin + prompt')

    # empty
    chat = pexpect.spawn(f'{python_path} {baize_path}')
    check(chat, 'empty', True)

    # previous
    chat = pexpect.spawn(f'{python_path} {baize_path} 你好 -p --log')
    check(chat, 'previous')

    # context
    chat = pexpect.spawn(f'{python_path} {baize_path} --setcontext 你好')
    check(chat, 'context1')
    chat = pexpect.spawn(f'{python_path} {baize_path} 我是小明 --log')
    check(chat, 'context2')

    # template
    chat = pexpect.spawn(f'{python_path} {baize_path} -t summary 你好')
    check(chat, 'template')

    # history
    chat = pexpect.spawn(f'{python_path} {baize_path} -H')
    check(chat, 'history')

    # file
    licence = os.path.join(os.path.dirname(baize_path), 'LICENSE')
    chat = pexpect.spawn(f'{python_path} {baize_path} 你好 -f {licence} --log')
    check(chat, 'file')

    # img
    banner = os.path.join(os.path.dirname(baize_path), 'banner.png')
    chat = pexpect.spawn(f'{python_path} {baize_path} 你好 -i {banner} --log')
    check(chat, 'img')


def test_output():
    console.print(Markdown('# Output Test'))

    # stream
    chat = pexpect.spawn(f'{python_path} {baize_path} 你好 -s')
    check(chat, 'stream')

    # markdown
    chat = pexpect.spawn(f'{python_path} {baize_path} 你好 -M')
    check(chat, 'markdown')

    # stream + markdown
    chat = pexpect.spawn(f'{python_path} {baize_path} 你好 -Ms')
    check(chat, 'stream + markdown')

    # copy
    pyperclip.copy('')
    chat = pexpect.spawn(f'{python_path} {baize_path} 你好 -C')
    check(chat, 'copy')
    assert(len(pyperclip.paste()) > 0)

    # output
    chat = pexpect.spawn(f'{python_path} {baize_path} 你好 -o __test__.txt')
    check(chat, 'output')
    assert(os.path.exists('__test__.txt'))
    os.remove('__test__.txt')


def test_cli_mode():
    console.print(Markdown('# Cli Mode Test'))

    # 单 prompt
    chat = pexpect.spawn(f'{python_path} {baize_path} -c 打印当前目录')
    chat.expect(':')
    chat.sendline('n')
    check(chat, '单 prompt')

    # 多 prompt
    chat = pexpect.spawn(f'{python_path} {baize_path} -c 打印 当前 目录')
    chat.expect(':')
    chat.sendline('n')
    check(chat, '多 prompt')

    # clidetail
    chat = pexpect.spawn(f'{python_path} {baize_path} 打印当前目录 --clidetail')
    chat.expect(':')
    chat.sendline('n')
    check(chat, 'clidetail')

    # clidetail + stream
    chat = pexpect.spawn(f'{python_path} {baize_path} 打印当前目录 --clidetail -s')
    chat.expect(':')
    chat.sendline('n')
    check(chat, 'clidetail + stream')


def test_workflow():
    console.print(Markdown('# Workflow Test'))

    # workflow
    chat = pexpect.spawn(f'{python_path} {baize_path} -w test')
    check(chat, 'workflow')

    # workflow + log
    chat = pexpect.spawn(f'{python_path} {baize_path} -w test --log')
    check(chat, 'workflow + log')


from utils.workflow.graph import Graph, print_graph
from utils.workflow.node import *
def workflow_unit_test():
    graph = Graph()
    node1 = EmptyNode('node1')
    node2 = EmptyNode('node2')
    node3 = EmptyNode('node3')

    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_node(node3)

    graph.edge('node1', 'node2')
    graph.edge('node2', 'node3')
    print_graph(graph)
    graph.check_loop()
    graph.edge('node3', 'node1')
    graph.remove_edge('node3', 'node1')
    print_graph(graph)
    graph.check_loop()
    graph.edge('node3', 'node1')
    graph.remove_node('node3')
    print_graph(graph)
    assert(graph.get_node('node1') == node1)

CODE = """
def print_test(name: str):
    # 打印
    # name: 名字
    print(name)
"""

def test_tool():
    console.print(Markdown('# Tool Test'))

    # tool create
    chat = pexpect.spawn(f'{python_path} {baize_path} --createtool')
    pyperclip.copy(CODE)
    chat.expect('.')
    chat.sendline()
    chat.expect('.')
    chat.sendline()
    chat.sendline('test_tool')
    chat.expect(':')
    chat.sendline('test_tool')
    chat.expect(':')
    chat.sendline('test_tool')
    chat.expect(':')
    chat.sendline()
    chat.expect(':')
    chat.sendline('y')
    check(chat, 'tool create')

    # tool delete
    chat = pexpect.spawn(f'{python_path} {baize_path} --deletetool test_tool')
    chat.expect(':')
    chat.sendline('y')
    check(chat, 'tool delete')

    # tool
    chat = pexpect.spawn(f'{python_path} {baize_path} --tool interpreter')
    chat.expect('>')
    chat.sendline('你好')
    chat.expect('>')
    chat.sendline('使用牛顿迭代法计算 x^3 = 5 的解')
    chat.expect('>')
    chat.sendline('/q')
    check(chat, 'tool')

    # tool + log
    chat = pexpect.spawn(f'{python_path} {baize_path} --tool interpreter --log')
    chat.expect('>')
    chat.sendline('你好')
    chat.expect('>')
    chat.sendline('现在的时间是什么时候？')
    chat.expect('>')
    chat.sendline('/q')
    check(chat, 'tool + log')


def test_update():
    console.print(Markdown('# Update Test'))

    chat = pexpect.spawn(f'{python_path} {baize_path} --update')
    index = chat.expect([':', 'v'])
    if index == 0:
        chat.sendline('n')
    check(chat, 'update')


if __name__ == "__main__":
    # 测试需要保证已经配置过一个名叫 test 的模型
    # 测试会使用 test 模型进行测试
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    if args.debug:
        debug = True

    print(f'python_path: {python_path}')
    print(f'baize_path:  {baize_path}')

    workflow_unit_test()

    test_settings()
    chat = pexpect.spawn(f'{python_path} {baize_path} --set test')
    time.sleep(3)
    test_input()
    test_output()
    test_cli_mode()
    test_workflow()
    test_tool()
    test_update()