from rich.console import Console
from rich import print as rprint
from pyboxmaker import box

console = Console()

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


def input_param(param_name: str) -> str:
    param = ''
    while len(param) == 0:
        rprint(f'请输入 [b green]{param_name}[/b green]: ', end='')
        param = input()
    return param


def input_setting() -> float | None:
    setting = None
    while setting is None:
        setting = input()
        if setting == '':
            return None
        try:
            setting = float(setting)
        except ValueError:
            print('请输入有效的数字')
            setting = None
    return setting


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

    if model_family == '自定义':
        while len(model_name) == 0:
            rprint('请输入 [b green]模型名称[/b green]: ', end='')
            model_name = input()
        while len(base_url) == 0:
            rprint('请输入 [b green]BASE_URL[/b green]: ', end='')
            base_url = input()
        rprint('请输入 [b green]API_KEY[/b green] (ENTER 空): ', end='')
        api_key = input()
    elif model_family == 'openai':
        model_name = choose_model(models['openai']['models'])
        base_url = models['openai']['base_url']
        api_key = input_param('API KEY')
    elif model_family == 'glm':
        model_name = choose_model(models['glm']['models'])
        base_url = models['glm']['base_url']
        api_key = input_param('API KEY')
    elif model_family == 'qwen':
        model_name = choose_model(models['qwen']['models'])
        base_url = models['qwen']['base_url']
        api_key = input_param('API KEY')
    elif model_family == 'deepseek':
        model_name = choose_model(models['deepseek']['models'])
        base_url = models['deepseek']['base_url']
        api_key = input_param('API KEY')
    elif model_family == 'doubao':
        rprint('[yellow]豆包大模型的模型选择由控制台的推理接入点控制[/yellow]')
        model_name = choose_model(models['doubao']['models'])
        base_url = models['doubao']['base_url']
        api_key = input_param('API KEY')
        endpoint_id = input_param('推理接入点 ID')
        config[model_name]['endpoint_id'] = endpoint_id
    else:
        raise ValueError('Unknown model family')

    rprint('请输入 [b green]temperature[/b green] (ENTER 默认): ', end='')
    temperature = input_setting()
    rprint('请输入 [b green]frequency penalty[/b green] (ENTER 默认): ', end='')
    frequency_penalty = input_setting()
    rprint('请输入 [b green]presence penalty[/b green] (ENTER 默认): ', end='')
    presence_penalty = input_setting()

    config['default_model'] = model_name
    config[model_name]['base_url'] = base_url

    if api_key != '':
        config[model_name]['api_key'] = api_key
    if temperature is not None:
        config[model_name]['temperature'] = temperature
    if frequency_penalty is not None:
        config[model_name]['frequency_penalty'] = frequency_penalty
    if presence_penalty is not None:
        config[model_name]['presence_penalty'] = presence_penalty

    print()
    print_config(model_name, config[model_name])

    save = ''
    while save != 'y' and save != 'n':
        save = input('是否保存配置? (y/n): ')

    if save == 'y':
        from utils.config import save_model_config
        save_model_config(config)