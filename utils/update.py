import os
import requests
import zipfile
from baize import ___VERSION___
from packaging import version
from rich import print as rprint
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TimeRemainingColumn,
)

GIT_URL = 'https://api.github.com/repos/Syan-Lin/baize/releases/latest'


def get_path(file: str):
    user_home = os.path.expanduser('~')
    root_path = os.path.join(user_home, 'baize', file)
    return root_path


def get_latest_release():
    response = requests.get(GIT_URL)
    response.raise_for_status()
    return response.json()


def download_asset(url: str, file_path: str):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    progress = Progress(
        '{task.description}',
        BarColumn(),
        DownloadColumn(),
        TimeRemainingColumn(),
    )

    with open(file_path, 'wb') as f:
        block_size = 1024
        total_size = int(response.headers.get('content-length', 0))

        with progress:
            task = progress.add_task(f'"{file_path}" 下载中...', total=total_size)
            while not progress.finished:
                progress.update(task, advance=block_size)
                buffer = response.raw.read(block_size)
                f.write(buffer)


def unpack_zip(file_path: str):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(os.path.join(os.path.expanduser('~'), 'baize'))

    zip_ref.close()
    os.remove(file_path)


def download_file(assets: list, file_name: str) -> bool:
    for asset in assets:
        if asset['name'] == file_name:
            file_path = get_path(file_name)
            download_asset(asset['browser_download_url'], file_path)
            unpack_zip(file_path)
            return True
    return False


def download_exec(assets: list) -> bool:
    import platform
    system_name = platform.system()
    if system_name == 'Linux':
        return download_file(assets, 'baize_linux.zip')
    elif system_name == 'Darwin':
        return download_file(assets, 'baize_mac.zip')
    elif system_name == 'Windows':
        return download_file(assets, 'baize_windows.zip')
    else:
        raise NotImplementedError(f'不支持的操作系统: {system_name}，请手动配置环境变量')


def update():
    release_info = get_latest_release()

    current_version = version.parse(___VERSION___)
    latest_version = version.parse(release_info['tag_name'])

    if current_version >= latest_version:
        rprint(f'[green]当前版本 v{current_version} 已是最新版本！[/green]')
        return

    print(f'最新版本 v{latest_version} 确认更新 [y/n]: ', end='')
    choice = ''
    choice = input()

    if choice == 'n':
        return

    baize_path = get_path('baize')
    backup_path = get_path('baize_bak')

    try:
        os.rename(baize_path, backup_path)
        assets = release_info['assets']
        if not download_file(assets, 'resource.zip'):
            rprint(f'[red]错误: 下载资源失败！[/red]')
            raise Exception
        if not download_exec(assets):
            rprint(f'[red]错误: 下载可执行文件失败！[/red]')
            raise Exception
    except:
        os.rename(backup_path, baize_path)
    os.remove(backup_path)
    os.chmod(baize_path, 0o755)