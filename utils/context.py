import os
import json
from rich import print as rprint


def save_previous(messages: list[dict], response: str):
    messages.append({"role": "assistant", "content": response})

    user_home = os.path.expanduser('~')
    history_path = os.path.join(user_home, 'baize', 'history.json')
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False)


def load_previous() -> list[dict]:
    user_home = os.path.expanduser('~')
    history_path = os.path.join(user_home, 'baize', 'history.json')
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
            return history

    return []


def load_context() -> str:
    user_home = os.path.expanduser('~')
    context_path = os.path.join(user_home, 'baize', 'context.md')
    if os.path.exists(context_path):
        with open(context_path, "r", encoding="utf-8") as f:
            context = f.read()
            return context

    return ''


def save_context(text: str):
    user_home = os.path.expanduser('~')
    context_path = os.path.join(user_home, 'baize', 'context.md')
    with open(context_path, "w", encoding="utf-8") as f:
        f.write(text)


def print_messages(messages: list[dict]):
    for message in messages:
        role = message["role"]
        content = message["content"]
        if role == 'assistant':
            rprint(f'[blue]{role}:\n{content}[/blue]')
        elif role == 'user':
            rprint(f'[green]{role}:\n{content}[/green]')
        else:
            rprint(f'[red]{role}:\n{content}[/red]')