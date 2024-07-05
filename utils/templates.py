import os
import json
from datetime import datetime
from rich import print as rprint
from utils.resource import print_resource_table, get_resource_path, get_resource_list, ResourceType


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
        template_root_path = get_resource_path(ResourceType.templates)
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
            }, f, ensure_ascii=False)
        with open(os.path.join(new_template_path, 'prompt.md'), 'w', encoding='utf-8') as f:
            f.write(template_content)
        info = f'模板创建成功！保存在目录 {new_template_path}'
        rprint('[green]' + info + '[/green]')