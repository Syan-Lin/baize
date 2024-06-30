import os
import json
import yaml
from rich import print as rprint
from utils.resource import get_root_path

def models_info() -> dict:
    '''获取所有支持的模型信息'''
    models_info_path = os.path.join(get_root_path(), 'models.json')

    if not os.path.exists(models_info_path):
        raise FileNotFoundError(f'路径 {models_info_path} 不存在, 请重新安装 baize。')

    with open(models_info_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def model_config() -> dict:
    '''获取所有已注册的模型信息'''
    config_path = os.path.join(get_root_path(), 'config.yaml')

    if not os.path.exists(config_path):
        return {}

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def set_default_config(model_name: str):
    config = model_config()
    if model_name not in list(config.keys()):
        raise ValueError(f'模型 {model_name} 未注册，无法设置为默认模型！')
    config['default_config'] = model_name
    save_model_config(config)
    rprint(f'[green]已将模型 {model_name} 设置为默认模型[/green]')


def save_model_config(config: dict):
    config_path = os.path.join(get_root_path(), 'config.yaml')

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)


def print_model_list():
    models = model_config()

    if len(models) == 0:
        rprint('[red]错误: 无模型可用，请执行[/red] [green]`baize --setup`[/green] [red]进行初始化[/red]')
        return

    used_model = models['default_config']
    models.pop('default_config')

    for model_name in models.keys():
        if model_name == used_model:
            rprint(f'[bold green]*{model_name}[/bold green]')
        else:
            print(model_name)