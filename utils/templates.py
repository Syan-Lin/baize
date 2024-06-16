from datetime import datetime
import os
import json
from rich import print as rprint


def get_template_path() -> str:
    user_home = os.path.expanduser('~')
    template_root_path = os.path.join(user_home, 'baize', 'templates')

    if not os.path.exists(template_root_path):
        raise FileNotFoundError(f'路径 {template_root_path} 不存在, 请重新安装 baize。')

    return template_root_path


def get_template(template_name: str) -> str:
    template_root_path = get_template_path()

    template_path = os.path.join(template_root_path, template_name)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f'模板 {template_path} 不存在！')

    prompt_path = os.path.join(template_path, 'prompt.md')
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f'模板 {prompt_path} 不存在！')

    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def get_list() -> list[dict]:
    template_root_path = get_template_path()

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


def print_template_table(template_list: list):
    from rich.table import Table
    from rich.console import Console

    table = Table(show_header=True, header_style="bold green")
    console = Console()

    table.add_column("模板名", style='blue', width=20)
    table.add_column("描述", width=50)
    table.add_column("作者", style='red', width=10)
    table.add_column("日期", style='yellow', width=10)

    for template in template_list:
        table.add_row(template['name'], template['describe'], template['author'], template['date'])
    console.print(table)


def print_template_list():
    template_list = get_list()
    print_template_table(template_list)


def create_template():
    import pyperclip
    rprint('准备开始创建模板，模板内容会自动从剪贴板获取，请确保 [green]剪贴板中已经复制[/green] 了模板内容，程序在输入任意键后开始...', end='')
    input()
    template_content = pyperclip.paste()
    rprint('请输入 [green]模板名称[/green]: ', end='')
    template_name = input()
    rprint('请用 [green]一句话[/green] 描述模板: ', end='')
    template_describe = input()
    rprint('请输入 [green]作者名[/green]: ', end='')
    author = input()
    date = datetime.now().strftime('%Y-%m-%d')

    rprint('\n[blue]模板内容[/blue]: ')
    from utils.render import print_markdown
    print_markdown(template_content)

    rprint('\n[blue]模板元信息[/blue]: ')

    template_list = [{
        'name': template_name,
        'describe': template_describe,
        'author': author,
        'date': date,
    }]

    print_template_table(template_list)

    choice = ''
    while choice != 'y' and choice != 'n':
        print('确认保存 [y/n]: ', end='')
        choice = input()

    if choice == 'y':
        template_root_path = get_template_path()
        new_template_path = os.path.join(template_root_path, template_name)
        if os.path.exists(new_template_path):
            rprint('[red]模板已存在，无法创建！[/red]')
            return
        os.makedirs(new_template_path)
        with open(os.path.join(new_template_path, 'meta.json'), 'w', encoding='utf-8') as f:
            json.dump({
                'describe': template_describe,
                'author': author,
                'date': date,
            }, f)
        with open(os.path.join(new_template_path, 'prompt.md'), 'w', encoding='utf-8') as f:
            f.write(template_content)
        info = f'模板创建成功！保存在目录 {new_template_path}'
        rprint('[green]' + info + '[/green]')


def delete_template(delete_templates: list[str]):
    template_list = get_list()

    def in_list(template: str) -> bool:
        for template_meta in template_list:
            if template == template_meta['name']:
                return True
        return False

    delete_list = []
    for template in delete_templates:
        if in_list(template):
            delete_list.append(template)
        else:
            rprint(f'[yellow]模板 {template} 不存在！[/yellow]')
    if len(delete_list) == 0:
        rprint(f'[yellow]没有模板需要删除！[/yellow]')
        return

    rprint('[red]即将删除以下模板：[/red]')
    delete_template_meta = []
    for template in delete_list:
        for template_meta in template_list:
            if template == template_meta['name']:
                delete_template_meta.append(template_meta)
                break
    print_template_table(delete_template_meta)

    rprint('[green]确认删除 [/green][y/n]: ', end='')
    choice = ''
    while choice != 'y' and choice != 'n':
        choice = input()

    if choice == 'y':
        for template in delete_list:
            import shutil
            shutil.rmtree(os.path.join(get_template_path(), template))
        rprint('[green]删除成功！[/green]', end='')