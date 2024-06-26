import os
import json


class ResourceType:
    templates = 'templates'
    workflow = 'workflow'
    tool = 'tool'


def get_resource_path(resource: str) -> str:
    user_home = os.path.expanduser('~')
    root_path = os.path.join(user_home, 'baize', resource)

    if not os.path.exists(root_path):
        raise FileNotFoundError(f'路径 {root_path} 不存在, 请重新安装 baize。')

    return root_path


def get_resource(resource: str, name: str) -> str:
    root_path = get_resource_path(resource)

    resource_path = os.path.join(root_path, name)
    if not os.path.exists(resource_path):
        raise FileNotFoundError(f'资源 {resource_path} 不存在！')

    if resource == ResourceType.templates:
        file = 'prompt.md'
    elif resource == ResourceType.workflow:
        file = 'workflow.json'
    elif resource == ResourceType.tool:
        file = 'tool.json'
    else:
        raise ValueError(f'未知资源: {resource}')

    file_path = os.path.join(resource_path, file)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'资源 {file_path} 不存在！')

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_resource_list(resource: str) -> list[dict]:
    root_path = get_resource_path(resource)

    resource_list = []
    for resource_name in os.listdir(root_path):
        resource_path = os.path.join(root_path, resource_name)
        if os.path.isdir(resource_path):
            meta_data_path = os.path.join(resource_path, 'meta.json')
            try:
                with open(meta_data_path, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                resource_list.append({
                    'name': resource_name,
                    'describe': meta_data['describe'],
                    'author': meta_data['author'],
                    'date': meta_data['date'],
                })
            except Exception as e:
                print(e)
                resource_list.append({
                    'name': resource_name,
                    'describe': '',
                    'author': '',
                    'date': '',
                })
    return resource_list


def print_resource_table(resource: str | list):
    from rich.table import Table
    from rich.console import Console
    if isinstance(resource, str):
        resource_list = get_resource_list(resource)
    else:
        resource_list = resource

    table = Table(show_header=True, header_style="bold green")
    console = Console()

    table.add_column("资源名", style='blue', width=20)
    table.add_column("描述", width=50)
    table.add_column("作者", style='red', width=10)
    table.add_column("日期", style='yellow', width=10)

    for resource in resource_list:
        table.add_row(resource['name'], resource['describe'], resource['author'], resource['date'])
    console.print(table)