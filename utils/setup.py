import os
from rich.console import Console
from rich import print as rprint
from pyboxmaker import box

console = Console()

def append_path(bash_file: str):
    file_path = os.path.expanduser(f'~/{bash_file}')

    if not os.path.exists(file_path):
        rprint(f'文件不存在: {file_path}')
        return

    root = os.path.expanduser('~')
    baize_path = os.path.join(root, 'baize')
    append_line = f'export PATH="$PATH:{baize_path}"'

    with open(file_path, 'r') as f:
        file_content = f.read()
    if append_line not in file_content:
        with open(file_path, 'a') as f:
            f.write(append_line + '\n')
        rprint(f'路径已写入: {file_path}，请重启终端')
    else:
        rprint(f'路径在 {file_path} 已存在，退出...')


def init_env(bash: str):
    import platform
    system_name = platform.system()

    if system_name == 'Linux':
        if bash == 'bash':
            append_path('.bashrc')
        elif bash == 'zsh':
            append_path('.zshrc')
        else:
            raise NotImplementedError(f'不支持的Shell: {bash}')
    elif system_name == 'Darwin':
        if bash == 'bash':
            append_path('.bash_profile')
        elif bash == 'zsh':
            append_path('.zshrc')
        else:
            raise NotImplementedError(f'不支持的Shell: {bash}')
    else:
        raise NotImplementedError(f'不支持的操作系统: {system_name}，请手动配置环境变量')


def choose_model_family(models: dict) -> int:
    print('选择产品族: ')
    for i, (_, value) in enumerate(models.items()):
        console.print(f'{i + 1}. {value['family']}', style='bold green')
    console.print(f'{len(models) + 1}. 自定义', style='bold green')

    choice = 0
    while choice <= 0 or choice > len(models) + 1:
        try:
            choice = int(input(f'请输入序号(1-{len(models) + 1}): '))
        except ValueError:
            print('请输入有效的数字')
    print()

    if choice == len(models) + 1:
        return '自定义'
    keys = list(models.keys())
    return keys[choice - 1]


def choose_model(model_list: list) -> str:
    print('选择模型: ')
    for i, model in enumerate(model_list):
        console.print(f'{i + 1}. "{model}"', style='bold green')

    choice = 0
    while choice <= 0 or choice > len(model_list):
        try:
            choice = int(input(f'请输入序号(1-{len(model_list)}): '))
        except ValueError:
            print('请输入有效的数字')
    print()

    return model_list[choice - 1]


def input_param(param_name: str, skip: bool = False) -> str | None:
    param = ''
    while len(param) == 0:
        if skip:
            rprint(f'请输入 [b green]{param_name}[/b green] (ENTER 默认): ', end='')
        else:
            rprint(f'请输入 [b green]{param_name}[/b green]: ', end='')
        param = input()
        if skip:
            if len(param) == 0:
                return None
            break
    return param


def print_config(model_name: str, config: dict):
    title = '✨ 您的模型配置 ✨'
    text = []
    text.append(f'模型名: \t\t{model_name}')

    for key, value in config.items():
        text.append(f'{key}: \t\t{value}')

    box(title=title, texts=text, title_color='green', box_color='green', title_align='upcenter')


def setup():
    from utils.config import models_info
    models = models_info()
    model_family = choose_model_family(models)

    from utils.config import model_config
    config = model_config()
    config_name = input_param('配置名')
    config['default_config'] = config_name
    config[config_name] = {}
    new_config = config[config_name]

    if model_family == '自定义':
        model_name = input_param('模型名')
        base_url = input_param('BASE_URL')
        api_key = input_param('API_KEY', True)
    elif model_family == 'doubao':
        rprint('[yellow]豆包大模型的模型选择由控制台的推理接入点控制[/yellow]')
        base_url = input_param('BASE_URL', True)
        api_key = input_param('API_KEY')
        endpoint_id = input_param('推理接入点 ID')
        new_config['endpoint_id'] = endpoint_id
    else:
        model_name = choose_model(models[model_family]['models'])
        base_url = input_param('BASE_URL', True)
        api_key = input_param('API_KEY')

    temperature = input_param('temperature', True)
    frequency_penalty = input_param('frequency penalty', True)
    presence_penalty = input_param('presence penalty', True)

    new_config['model_name'] = model_name
    new_config['api_key'] = api_key
    if base_url is None:
        new_config['base_url'] = models[model_family]['base_url']
    else:
        new_config['base_url'] = base_url
    if temperature is not None:
        new_config['temperature'] = temperature
    if frequency_penalty is not None:
        new_config['frequency_penalty'] = frequency_penalty
    if presence_penalty is not None:
        new_config['presence_penalty'] = presence_penalty

    print()
    print_config(config_name, new_config)

    save = ''
    while save != 'y' and save != 'n':
        save = input('保存配置 [y/n]: ')

    if save == 'y':
        from utils.config import save_model_config
        save_model_config(config)