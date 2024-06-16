import os
import shutil
import sys
from rich.console import Console
from importlib.metadata import distributions


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
    if not is_package_installed('pyinstaller'):
        print('请先安装 pyinstaller 再执行该程序')
        sys.exit()
    user_home = os.path.expanduser('~')
    base_dir = os.path.join(user_home, 'baize')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    console = Console()

    with console.status("[bold green]PyInstaller 构建二进制程序...", spinner="toggle4") as status:
        import subprocess
        result = subprocess.run('pyinstaller --onefile baize.py', capture_output=True, text=True, shell=True, encoding='utf-8')
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)

    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    excute_file = os.listdir(os.path.join(script_dir, 'dist'))[0]
    excute_path = os.path.join(script_dir, 'dist', excute_file)

    shutil.copy(excute_path, os.path.join(base_dir, excute_file))

    shutil.rmtree(os.path.join(script_dir, 'dist'))
    shutil.rmtree(os.path.join(script_dir, 'build'))
    os.remove(os.path.join(script_dir, 'baize.spec'))

    copy_config_files(base_dir)
    copy_template_files(base_dir)

    print(f'程序已被安装至 `{base_dir}`，请手动将程序添加至环境变量中')