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


def input_api_key() -> str:
    api_key = ''
    while len(api_key) == 0:
        rprint('请输入 [b green]API_KEY[/b green]: ', end='')
        api_key = input()
    return api_key


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


def print_config(model_family: str, model_name: str, base_url: str, api_key: str,
                 temperature: float | None, frequency_penalty: float | None, presence_penalty: float | None):
    title = '✨ 您的模型配置 ✨'
    text = []
    text.append(f'产品族: \t\t{model_family}')
    text.append(f'模型名: \t\t{model_name}')
    if base_url != '':
        text.append(f'BASE_URL: \t\t{base_url}')
    else:
        text.append(f'BASE_URL: \t\t默认')
    if api_key != '':
        text.append(f'API_KEY: \t\t{api_key}')
    else:
        text.append(f'API_KEY: \t\tNone')
    if temperature is None:
        text.append('temperature: \t\t默认')
    else:
        text.append(f'temperature: \t\t{temperature}')
    if frequency_penalty is None:
        text.append('frequency penalty: \t默认')
    else:
        text.append(f'frequency penalty: \t{frequency_penalty}')
    if presence_penalty is None:
        text.append('presence penalty: \t默认')
    else:
        text.append(f'presence penalty: \t{presence_penalty}')

    box(title=title, texts=text, title_color='green', box_color='green', title_align='upcenter')


def setup():
    from utils.config import models_info
    models = models_info()
    model_family = choose_model_family(models)

    model_name, base_url = '', ''
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
        api_key = input_api_key()
    elif model_family == 'glm':
        model_name = choose_model(models['glm']['models'])
        api_key = input_api_key()
    elif model_family == 'qwen':
        model_name = choose_model(models['qwen']['models'])
        api_key = input_api_key()
    elif model_family == 'deepseek':
        model_name = choose_model(models['deepseek']['models'])
        api_key = input_api_key()
    else:
        raise ValueError('Unknown model family')

    rprint('请输入 [b green]temperature[/b green] (ENTER 默认): ', end='')
    temperature = input_setting()
    rprint('请输入 [b green]frequency penalty[/b green] (ENTER 默认): ', end='')
    frequency_penalty = input_setting()
    rprint('请输入 [b green]presence penalty[/b green] (ENTER 默认): ', end='')
    presence_penalty = input_setting()

    print()
    print_config(model_family, model_name, base_url, api_key, temperature, frequency_penalty, presence_penalty)

    from utils.config import model_config
    config = model_config()
    config['default_model'] = model_name
    config[model_name] = {}

    if api_key != '':
        config[model_name]['api_key'] = api_key
    if base_url != '':
        config[model_name]['base_url'] = base_url
    if temperature is not None:
        config[model_name]['temperature'] = temperature
    if frequency_penalty is not None:
        config[model_name]['frequency_penalty'] = frequency_penalty
    if presence_penalty is not None:
        config[model_name]['presence_penalty'] = presence_penalty

    save = ''
    while save != 'y' and save != 'n':
        save = input('是否保存配置? (y/n): ')

    if save == 'y':
        from utils.config import save_model_config
        save_model_config(config)