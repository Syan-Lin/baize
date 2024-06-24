import os
import json
from argparse import Namespace
from workflow.graph import init_graph


def get_workflow_path() -> str:
    user_home = os.path.expanduser('~')
    workflow_root_path = os.path.join(user_home, 'baize', 'workflow')
    return workflow_root_path


def get_workflow_list() -> list[str]:
    workflow_root_path = get_workflow_path()

    workflow_list = []
    for workflow_name in os.listdir(workflow_root_path):
        workflow_path = os.path.join(workflow_root_path, workflow_name)
        if os.path.isdir(workflow_path):
            meta_data_path = os.path.join(workflow_path, 'meta.json')
            try:
                with open(meta_data_path, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                workflow_list.append({
                    'name': workflow_name,
                    'describe': meta_data['describe'],
                    'author': meta_data['author'],
                    'date': meta_data['date'],
                })
            except Exception as e:
                print(e)
                workflow_list.append({
                    'name': workflow_name,
                    'describe': '',
                    'author': '',
                    'date': '',
                })
    return workflow_list


def print_workflow_table():
    from rich.table import Table
    from rich.console import Console

    workflow_list = get_workflow_list()

    table = Table(show_header=True, header_style="bold green")
    console = Console()

    table.add_column("工作流名", style='blue', width=20)
    table.add_column("描述", width=50)
    table.add_column("作者", style='red', width=10)
    table.add_column("日期", style='yellow', width=10)

    for workflow in workflow_list:
        table.add_row(workflow['name'], workflow['describe'], workflow['author'], workflow['date'])
    console.print(table)


def get_workflow(workflow_name: str) -> str:
    user_home = os.path.expanduser('~')
    workflow_root_path = os.path.join(user_home, 'baize', 'workflow')

    if not os.path.exists(workflow_root_path):
        raise FileNotFoundError(f'路径 {workflow_root_path} 不存在, 请重新安装 baize。')

    workflow_path = os.path.join(workflow_root_path, workflow_name)
    if not os.path.exists(workflow_path):
        raise FileNotFoundError(f'Workflow {workflow_name} 不存在。')

    with open(os.path.join(workflow_path, 'workflow.json'), 'r', encoding='utf-8') as f:
        workflow_config = json.load(f)

    return workflow_config


def workflow_main(args: Namespace):
    workflow_config = get_workflow(args.workflow[0])
    workflow = init_graph(workflow_config, args.log)
    workflow.run()