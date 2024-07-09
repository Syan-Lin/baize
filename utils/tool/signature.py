import ast
import sys
import astor
from rich import print as rprint


def is_comment(line: str) -> bool:
    '''仅支持单行注释 #'''
    return line.strip().startswith('#')


def get_enums(source_code: str) -> dict:
    tree = ast.parse(source_code)
    enums = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.bases[0].attr != 'Enum':
                continue
            values = []
            for assign in node.body:
                values.append(assign.value.value)
            enums[node.name] = values
    return enums


def get_descriptions(source_code: str, function: ast.FunctionDef) -> tuple[str, list]:
    lineno = function.lineno
    lines = source_code.split('\n')
    if not is_comment(lines[lineno]):
        rprint(f'[red]错误: 函数 {function.name} 缺少注释描述！[/red]')
        sys.exit()
    function_description = lines[lineno].strip().strip('#').strip()

    args_description = []
    for i, arg in enumerate(function.args.args):
        if not is_comment(lines[lineno + i + 1]):
            rprint(f'[red]错误: 函数 {function.name} 的参数 {arg.arg} 缺少注释描述！[/red]')
            sys.exit()
        arg_desc = lines[lineno + i + 1].strip().strip('#').strip()
        arg_desc = arg_desc.strip(arg.arg).strip().strip(':').strip('：').strip('-').strip()
        args_description.append(arg_desc)

    return function_description, args_description


def get_default_value(source_code: str, function: ast.FunctionDef) -> list:
    lineno = function.lineno
    lines = source_code.split('\n')
    defaults = []
    for i, arg in enumerate(function.args.args):
        begin = arg.end_col_offset
        end = -1 if i == len(function.args.args) - 1 else function.args.args[i+1].col_offset

        default_value = lines[lineno-1][begin:end]
        default_value = default_value.strip().strip('=').strip(',').strip(')').strip()

        if default_value != '':
            defaults.append({'arg': arg.arg, 'value': default_value})

    return defaults


def get_function_signatures(source_code) -> list[dict]:
    tree = ast.parse(source_code)
    enums = get_enums(source_code)

    function_signatures = []

    for function in ast.walk(tree):
        if isinstance(function, ast.FunctionDef):
            function_description, args_description = get_descriptions(source_code, function)
            signature = {
                'type': 'function',
                'function': {
                    'name': function.name,
                    'description': function_description,
                    'parameters': {}
                }
            }
            if len(args_description) > 0:
                signature['function']['parameters']['type'] = 'object'

                default_values = get_default_value(source_code, function)
                signature['function']['parameters']['required'] = []
                for i in range(len(function.args.args) - len(default_values)):
                    signature['function']['parameters']['required'].append(function.args.args[i].arg)

            signature['function']['parameters']['properties'] = {}
            for i, arg in enumerate(function.args.args):
                arg_name = arg.arg
                try:
                    arg_type = astor.to_source(arg.annotation).strip()
                except:
                    rprint(f'[red]错误: 函数 {function.name} 的参数 {arg_name} 需要标注类型！[/red]')
                    sys.exit()
                signature['function']['parameters']['properties'][arg_name] = {
                    'type': arg_type,
                    'description': args_description[i],
                }
                if arg_type in enums.keys():
                    signature['function']['parameters']['properties'][arg_name]['enum'] = enums[arg_type]
            function_signatures.append(signature)

    return function_signatures
