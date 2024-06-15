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