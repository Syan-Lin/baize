import os
import sys
import json
from rich import print as rprint
from argparse import Namespace
from utils.workflow.graph import init_graph, Graph, print_graph, graph2config
from utils.resource import get_resource, ResourceType, print_resource_table, get_resource_path, parse_paste
from utils.setup import input_param
from utils.workflow.node import (
    make_input_node,
    make_llm_node,
    make_output_node,
    make_script_node
)


def init_input_config():
    input_params = {'output': {}}
    param_num = int(input_param('参数量'))
    for _ in range(param_num):
        param_name = input_param('参数名')
        content = input_param('content（默认表示使用时输入）', True)
        if content is None:
            input_params['output'][param_name] = {'content': content}
        else:
            input_params['output'][param_name] = {'content': parse_paste(content)}
    return input_params


def init_llm_config():
    config = input_param('config', True)
    template = input_param('模板', True)
    content = input_param('Prompt', True)
    system = input_param('系统 Prompt', True)
    output = input_param('输出变量名')

    if template is None and content is None:
        rprint(f'[red]错误: 需要模板或 Prompt 参数[/red]')
        return

    llm_config = {}
    if config is not None:
        llm_config['config'] = parse_paste(config)
    if template is not None:
        llm_config['template'] = parse_paste(template)
    if content is not None:
        llm_config['content'] = parse_paste(content)
    if system is not None:
        llm_config['system'] = parse_paste(system)
    llm_config['output'] = parse_paste(output)

    return llm_config


def init_script_config():
    script = input_param('脚本路径')
    function = input_param('函数名')
    python = input_param('python 路径', True)
    output = input_param('输出变量名')

    python_path = 'python'
    if python is not None:
        python_path = python

    script_config = {}
    script_config['python'] = parse_paste(python_path)
    script_config['script'] = parse_paste(script)
    script_config['function'] = parse_paste(function)
    script_config['output'] = parse_paste(output)

    return script_config


def init_output_config():
    to = input_param('输出到')
    return {'to': parse_paste(to)}


def add_node(graph: Graph, command: str):
    if len(command) > 3:
        rprint(f'[red]错误: 节点创建格式为: /node <type> <name>[/red]')
        return
    node_type = command[1]
    node_name = command[2]
    if node_type == 'input':
        node = make_input_node(node_name, init_input_config())
    elif node_type == 'llm':
        node = make_llm_node(node_name, init_llm_config())
    elif node_type == 'script':
        node = make_script_node(node_name, init_script_config())
    elif node_type == 'output':
        node = make_output_node(node_name, init_output_config())
    else:
        rprint(f'[red]错误: 节点 {node_name} 类型错误，不存在类型 {node_type}[/red]')
        return
    graph.add_node(node)
    if node_type == 'input':
        graph.edge('root', node_name)
    return graph


def save_workflow(workflow_config: dict):
    workflow_name = input_param('Workflow 名称')
    workflow_describe = input_param('Workflow 描述', skip=True)
    author = input_param('作者', skip=True)
    from datetime import datetime
    date = datetime.now().strftime('%Y-%m-%d')

    rprint('\n[blue]模板元信息[/blue]: ')

    workflow_list = [{
        'name': workflow_name,
        'describe': workflow_describe,
        'author': author,
        'date': date,
    }]

    print_resource_table(workflow_list)

    choice = ''
    while choice != 'y' and choice != 'n':
        print('确认保存 [y/n]: ', end='')
        choice = input()

    if choice == 'y':
        workflow_root_path = get_resource_path(ResourceType.workflow)
        new_workflow_path = os.path.join(workflow_root_path, workflow_name)
        if os.path.exists(new_workflow_path):
            rprint('[red]错误: Workflow 已存在，无法创建！[/red]')
            return
        os.makedirs(new_workflow_path)
        with open(os.path.join(new_workflow_path, 'meta.json'), 'w', encoding='utf-8') as f:
            json.dump({
                'describe': workflow_describe,
                'author': author,
                'date': date,
            }, f, ensure_ascii=False)
        with open(os.path.join(new_workflow_path,'workflow.json'), 'w', encoding='utf-8') as f:
            json.dump(workflow_config, f, ensure_ascii=False)
        info = f'Workflow 创建成功！保存在目录 {new_workflow_path}'
        rprint('[green]' + info + '[/green]')


def create_workflow():
    from utils.workflow.node import EmptyNode
    workflow = Graph()
    workflow.add_node(EmptyNode('root'))

    while True:
        command = input('> ').strip()
        if command == '':
            continue
        command = command.split()
        if command[0] == '/addnode':
            workflow = add_node(workflow, command)
        elif command[0] == '/delnode':
            if len(command) > 2:
                rprint(f'[red]错误: 节点创建格式为: /delnode <name>[/red]')
                return
            workflow.remove_node(command[1])
        elif command[0] == '/edge':
            if len(command) > 3:
                rprint(f'[red]错误: 节点创建格式为: /edge <from_node> <to_node>[/red]')
                return
            workflow.edge(command[1], command[2])
        elif command[0] == '/deledge':
            if len(command) > 3:
                rprint(f'[red]错误: 节点创建格式为: /edge <from_node> <to_node>[/red]')
                return
            workflow.remove_edge(command[1], command[2])
            workflow.remove_edge(command[2], command[1])
        elif command[0] == '/save':
            workflow.remove_node('root')
            print(len(workflow.nodes))
            save_workflow(graph2config(workflow))
        elif command[0] == '/show':
            print_graph(workflow)
        elif command[0] == '/h':
            print('增加节点 /addnode <type> <name>')
            print('删除节点 /delnode <name>')
            print('增加边 /edge <from_node> <to_node>')
            print('删除边 /deledge <node1> <node2>')
            print('保存 /save <workflow name>')
            print('打印当前图 /show')
            print('粘贴(常驻指令) /p')
            print('退出 /q')
            print('帮助 /h')
        elif command[0] == '/q':
            break
        else:
            rprint(f'[red]错误: 不支持的指令[/red]')


def workflow_main(args: Namespace):
    if args.createworkflow:
        create_workflow()
        sys.exit()
    workflow_name = ''
    if args.showworkflow:
        workflow_name = args.showworkflow[0]
    else:
        workflow_name = args.workflow[0]

    workflow_config = get_resource(ResourceType.workflow, workflow_name)
    workflow_config = json.loads(workflow_config)
    workflow = init_graph(workflow_config, args.log)

    if args.showworkflow:
        print_graph(workflow)
        sys.exit()

    workflow.run()