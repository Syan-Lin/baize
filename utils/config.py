import os
import json
import yaml

def models_info():
    user_home = os.path.expanduser('~')
    models_info_path = os.path.join(user_home, 'baize', 'models.json')

    if not os.path.exists(models_info_path):
        raise FileNotFoundError(f'{models_info_path} not found, please reinstall baize.')

    with open(models_info_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def model_config():
    user_home = os.path.expanduser('~')
    config_path = os.path.join(user_home, 'baize', 'config.yaml')

    if not os.path.exists(config_path):
        return {}

    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_model_config(config: dict):
    user_home = os.path.expanduser('~')
    config_path = os.path.join(user_home, 'baize', 'config.yaml')

    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)