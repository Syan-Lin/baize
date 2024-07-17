import os
import json
from rich import print as rprint


class ResourceType:
    templates = 'templates'
    workflow = 'workflow'
    tool = 'tool'


def parse_paste(input: str):
    import pyperclip
    input = input.strip()
    if input == '/p':
        return pyperclip.paste()
    return input


def get_root_path() -> str:
    user_home = os.path.expanduser('~')
    root_path = os.path.join(user_home, '.baize')

    if not os.path.exists(root_path):
        os.makedirs(root_path)

    return root_path


def delete_resource(resource_type: str, delete_names: list[str]):
    resource_list = get_resource_list(resource_type)
    if resource_type == ResourceType.templates:
        resource_name = '模板'
    elif resource_type == ResourceType.workflow:
        resource_name = '流程'
    elif resource_type == ResourceType.tool:
        resource_name = '工具'
    else:
        raise ValueError(f'未知资源: {resource_type}')

    def in_list(resource: str) -> bool:
        for resource_meta in resource_list:
            if resource == resource_meta['name']:
                return True
        return False

    delete_list = []
    for resource in delete_names:
        if in_list(resource):
            delete_list.append(resource)
        else:
            rprint(f'[yellow]{resource_name} {resource} 不存在！[/yellow]')
    if len(delete_list) == 0:
        rprint(f'[yellow]没有{resource_name}需要删除！[/yellow]')
        return

    rprint(f'[red]即将删除以下{resource_name}：[/red]')
    delete_resource_meta = []
    for resource in delete_list:
        for resource_meta in resource_list:
            if resource == resource_meta['name']:
                delete_resource_meta.append(resource_meta)
                break
    print_resource_table(delete_resource_meta)

    print('确认删除 [y/n]: ', end='')
    choice = ''
    while choice != 'y' and choice != 'n':
        choice = input()

    if choice == 'y':
        for resource in delete_list:
            import shutil
            shutil.rmtree(os.path.join(get_resource_path(resource_type), resource))
        rprint('[green]删除成功！[/green]')


def get_resource_path(resource: str) -> str:
    root_path = os.path.join(get_root_path(), resource)

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