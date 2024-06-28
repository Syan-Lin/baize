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


def get_latest_release():
    response = requests.get(GIT_URL)
    response.raise_for_status()
    return response.json()


def download_asset(url: str, filename: str):
    response = requests.get(url, stream=True)
    response.raise_for_status()

    progress = Progress(
        '{task.description}',
        BarColumn(),
        DownloadColumn(),
        TimeRemainingColumn(),
    )

    with open(filename, 'wb') as f:
        block_size = 1024
        total_size = int(response.headers.get('content-length', 0))

        with progress:
            task = progress.add_task(f'"{filename}" 下载中...', total=total_size)
            while not progress.finished:
                progress.update(task, advance=block_size)
                buffer = response.raw.read(block_size)
                f.write(buffer)


def unpack_zip(filename: str):
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('.')

    zip_ref.close()
    os.remove(filename)


def download_file(assets: list, file_name: str) -> bool:
    for asset in assets:
        if asset['name'] == file_name:
            download_asset(asset['browser_download_url'], file_name)
            unpack_zip(file_name)
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

    assets = release_info['assets']
    if not download_file(assets, 'resource.zip'):
        rprint(f'[red]错误: 下载资源失败！[/red]')
        return
    if not download_exec(assets):
        rprint(f'[red]错误: 下载可执行文件失败！[/red]')
        return