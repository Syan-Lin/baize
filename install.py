import os
import shutil
import sys
import json

def copy_config_files(base_dir: str):
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    model_dir = os.path.join(script_dir, 'llm')
    model_config = os.path.join(model_dir, 'models.json')
    if not os.path.exists(model_config):
        raise FileNotFoundError(f'文件 {model_config} 不存在！')
    shutil.copy(model_config, base_dir)


def copy_template_files(base_dir: str):
    template_dir = os.path.join(base_dir, 'templates')
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
    source_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), 'templates')

    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path):
            shutil.copytree(item_path, os.path.join(template_dir, item))


if __name__ == "__main__":
    user_home = os.path.expanduser('~')
    base_dir = os.path.join(user_home, 'baize')

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    copy_config_files(base_dir)
    copy_template_files(base_dir)