import os
import json
from rich import print as rprint
from utils.resource import get_root_path


def save_previous(messages: list[dict], response: str = ''):
    if response != '':
        messages.append({"role": "assistant", "content": response})

    history_path = os.path.join(get_root_path(), 'history.json')
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False)


def load_previous() -> list[dict]:
    history_path = os.path.join(get_root_path(), 'history.json')
    if os.path.exists(history_path):
        with open(history_path, "r", encoding="utf-8") as f:
            history = json.load(f)
            return history

    return []


def load_context() -> str:
    context_path = os.path.join(get_root_path(), 'context.md')
    if os.path.exists(context_path):
        with open(context_path, "r", encoding="utf-8") as f:
            context = f.read()
            return context

    return ''


def save_context(text: str):
    context_path = os.path.join(get_root_path(), 'context.md')
    with open(context_path, "w", encoding="utf-8") as f:
        f.write(text)


def print_messages(messages: list[dict]):
    for message in messages:
        role = message["role"]
        content = message["content"]
        if role == 'assistant':
            if 'tool_calls' in message and message['tool_calls'] is not None:
               rprint(f'[blue]{role}:\n{message['tool_calls']}[/blue]\n')
            else:
                rprint(f'[blue]{role}:\n{content}[/blue]\n')
        elif role == 'user':
            rprint(f'[green]{role}:\n{content}[/green]\n')
        else:
            rprint(f'[red]{role}:\n{content}[/red]\n')