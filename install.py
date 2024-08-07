import os
import shutil
import sys
from rich.console import Console
from importlib.metadata import distributions
from utils.resource import ResourceType, get_root_path
from rich import print as rprint


def is_package_installed(package_name):
    for pkg in distributions():
        if pkg.metadata['Name'].lower() == package_name:
            return True
    return False


def copy_config_files(base_dir: str):
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    model_dir = os.path.join(script_dir, 'llm')
    model_config = os.path.join(model_dir, 'models.json')
    shutil.copy(model_config, base_dir)


def copy_resource_files(base_dir: str, resource_type: str):
    resource_dir = os.path.join(base_dir, resource_type)
    if not os.path.exists(resource_dir):
        os.makedirs(resource_dir)
    else:
        shutil.rmtree(resource_dir)
        os.makedirs(resource_dir)

    source_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), resource_type)
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path):
            shutil.copytree(item_path, os.path.join(resource_dir, item))


if __name__ == "__main__":
    if not is_package_installed('pyinstaller'):
        print('请先安装 pyinstaller 再执行该程序')
        sys.exit()
    root_path = get_root_path()

    console = Console()

    with console.status("[bold green]PyInstaller 构建二进制程序...", spinner="toggle4") as status:
        import subprocess
        result = subprocess.run('pyinstaller baize.py', capture_output=True, text=True, shell=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    dist_dir = os.path.join(script_dir, 'dist')
    excute_file = os.listdir(dist_dir)[0]

    shutil.copytree(os.path.join(dist_dir, excute_file), os.path.join(root_path), dirs_exist_ok=True)

    shutil.rmtree(os.path.join(script_dir, 'dist'))
    shutil.rmtree(os.path.join(script_dir, 'build'))
    os.remove(os.path.join(script_dir, 'baize.spec'))

    copy_config_files(root_path)
    copy_resource_files(root_path, ResourceType.templates)
    copy_resource_files(root_path, ResourceType.workflow)
    copy_resource_files(root_path, ResourceType.tool)

    rprint(f'程序已被安装至 [green]`{root_path}`[/green]，请手动将程序添加至环境变量中')