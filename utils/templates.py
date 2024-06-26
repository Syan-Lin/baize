import os
import json
from datetime import datetime
from rich import print as rprint
from utils.resource import print_resource_table, get_resource_path, get_resource_list


def expand_prompt(input_prompt: list[str]) -> str:
    prompt = ''
    for seg in input_prompt:
        prompt += seg + ' '
    return prompt


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

    print_resource_table(template_list)

    choice = ''
    while choice != 'y' and choice != 'n':
        print('确认保存 [y/n]: ', end='')
        choice = input()

    if choice == 'y':
        template_root_path = get_resource_path('templates')
        new_template_path = os.path.join(template_root_path, template_name)
        if os.path.exists(new_template_path):
            rprint('[red]错误: 模板已存在，无法创建！[/red]')
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
    template_list = get_resource_list('templates')

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
    print_resource_table(delete_template_meta)

    print('确认删除 [y/n]: ', end='')
    choice = ''
    while choice != 'y' and choice != 'n':
        choice = input()

    if choice == 'y':
        for template in delete_list:
            import shutil
            shutil.rmtree(os.path.join(get_resource_path('templates'), template))
        rprint('[green]删除成功！[/green]')