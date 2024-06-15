import os
import json
from rich import print as rprint

def get_template(template_name: str) -> str:
    user_home = os.path.expanduser('~')
    template_root_path = os.path.join(user_home, 'baize', 'templates')

    if not os.path.exists(template_root_path):
        raise FileNotFoundError(f'路径 {template_root_path} 不存在, 请重新安装 baize。')

    template_path = os.path.join(template_root_path, template_name)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f'模板 {template_path} 不存在！')

    prompt_path = os.path.join(template_path, 'prompt.md')
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f'模板 {prompt_path} 不存在！')

    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_list() -> list[dict]:
    user_home = os.path.expanduser('~')
    template_root_path = os.path.join(user_home, 'baize', 'templates')

    if not os.path.exists(template_root_path):
        raise FileNotFoundError(f'路径 {template_root_path} 不存在, 请重新安装 baize。')

    template_list = []
    for template_name in os.listdir(template_root_path):
        template_path = os.path.join(template_root_path, template_name)
        if os.path.isdir(template_path):
            meta_data_path = os.path.join(template_path, 'meta.json')
            try:
                with open(meta_data_path, 'r', encoding='utf-8') as f:
                    meta_data = json.load(f)
                template_list.append({
                    'name': template_name,
                    'describe': meta_data['describe'],
                    'author': meta_data['author'],
                    'date': meta_data['date'],
                })
            except Exception as e:
                print(e)
                template_list.append({
                    'name': template_name,
                    'describe': '',
                    'author': '',
                    'date': '',
                })
    return template_list


def print_template_list():
    from rich.table import Table
    from rich.console import Console

    table = Table(show_header=True, header_style="bold green")
    console = Console()
    template_list = get_list()

    table.add_column("模板名", style='blue', width=20)
    table.add_column("描述", width=50)
    table.add_column("作者", style='red', width=10)
    table.add_column("日期", style='yellow', width=10)

    for template in template_list:
        table.add_row(template['name'], template['describe'], template['author'], template['date'])
    console.print(table)