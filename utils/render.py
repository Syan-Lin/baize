from typing import Generator
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax

console = Console()

def print_markdown(text: str):
    markdown = Markdown(text)
    console.print(markdown)


def print_code(code: str, language: str):
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print(syntax)


def print_markdown_stream(generator: Generator) -> str:
    '''Markdown 打印时预留六行用 live 更新（直接 print 有可能丢失样式），剩余的使用 print 打印'''
    buffer_line = 6
    text = ''
    printed_line = 0

    from rich.text import Text
    from rich.live import Live
    import io
    string_io = io.StringIO()
    ansi = Console(file=string_io, force_terminal=True)

    live = Live()
    live.start()

    for block in generator:
        text += block

        # 获取 Markdown ANSI 表示
        markdown = Markdown(text)
        ansi.print(markdown)
        ansi_text = string_io.getvalue()
        string_io.truncate(0)
        string_io.seek(0)
        lines = ansi_text.splitlines(keepends=True)

        line_for_print = len(lines) - buffer_line
        if line_for_print > printed_line:
            ready_text = lines[printed_line:line_for_print]
            ready_text = ''.join(ready_text)
            live.console.print(Text.from_ansi(ready_text))
            printed_line = line_for_print

        if line_for_print < 0:
            line_for_print = 0
        rest = lines[line_for_print:]
        rest = ''.join(rest)
        live.update(Text.from_ansi(rest))

    live.stop()
    return text