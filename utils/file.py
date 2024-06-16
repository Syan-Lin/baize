import pdfplumber
import os


def pdf2str(file_path: str) -> str:
    result = ''
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            result += f'Page {i+1}:\n {page.extract_text()}\n\n'
    return result


def parse_file(file_path: list | str) -> list[str]:
    if isinstance(file_path, str):
        file_path = [file_path]

    result = []
    for file in file_path:
        file_name = os.path.basename(file)
        file_content = f'```{file_name}\n'
        if file.endswith('.pdf'):
            file_content += pdf2str(file)
        else:
            with open(file, 'r', encoding='utf-8') as f:
                file_content += f.read()
        file_content += '\n```\n'
        result.append(file_content)
    return result