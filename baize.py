import sys
from llm.base_llm import BaseLLM
from utils.render import print_markdown
from rich import print as rprint
from argparse import Namespace


def get_llm(model_name: str, model_config: dict) -> BaseLLM:
    from utils.config import models_info
    models = models_info()
    if model_name in models['qwen']['models']:
        from llm.qwen import Qwen
        llm = Qwen(model_name, model_config)
    elif model_name in models['openai']['models']:
        from llm.openai import GPT
        llm = GPT(model_name, model_config)

    return llm


def config_model(args: Namespace):
    from utils.config import model_config
    config = model_config()
    if args.model:
        set_model = args.model[0]
    else:
        if 'default_model' not in config.keys():
            rprint('[red]请先运行 `baize --setup` 配置模型[/red]')
            sys.exit()
        set_model = config['default_model']
    if set_model not in list(config.keys()):
        rprint(f'[red]未找到模型 {set_model}[/red]')
        sys.exit()
    llm = get_llm(set_model, config[set_model])
    return llm


def setting_args_parse(args: Namespace):
    if args.setup:
        from utils.setup import setup
        setup()
        sys.exit()
    elif args.modellist:
        from utils.config import print_model_list
        print_model_list()
        sys.exit()
    elif args.set:
        from utils.config import set_default_model
        set_default_model(args.set[0])
        sys.exit()
    elif args.list:
        from utils.templates import print_template_list
        print_template_list()
        sys.exit()
    elif args.context:
        from utils.context import load_context
        context = load_context()
        if context != '':
            print_markdown(context)
        else:
            print('Context 未设置')
        sys.exit()
    elif args.workflowlist:
        print('workflowlist')
        sys.exit()
    elif args.setcontext:
        from utils.context import save_context
        save_context(args.setcontext[0])
        sys.exit()
    elif args.resetcontext:
        from utils.context import save_context
        save_context('')
        sys.exit()


def input_args_parse(args: Namespace, llm: BaseLLM) -> list[dict]:
    # Prompt 输入
    if args.prompt:
        input_prompt = args.prompt
    else:
        input_prompt = [sys.stdin.read()]
    if args.paste:
        import pyperclip
        input_prompt = [pyperclip.paste()]

    messages = []

    # Context 引入
    from utils.context import load_context
    context = load_context()
    if context != '':
        messages.append({'role': 'system', 'content': context})

    # 历史对话引入
    if args.previous:
        from utils.context import load_previous
        history = load_previous()
        if len(history) > 0:
            messages += history

    # 构造模板
    template = None
    if args.templates:
        from utils.templates import get_template
        template = get_template(args.templates[0])

    if template is None:
        user_message = {'role': 'user', 'content': input_prompt[0]}
    else:
        try:
            template_format = template.format(input_prompt)
        except Exception as e:
            print(e)
            sys.exit()
        user_message = {'role': 'user', 'content': template_format}

    # 文件引入
    if args.file:
        try:
            file_message = llm.upload_file(args.file, user_message)
            messages.append(file_message)
        except NotImplementedError:
            rprint(f'[red]模型 {llm.model_name} 不支持文件上传[/red]')
            sys.exit()
    if args.img:
        try:
            img_message = llm.upload_img(args.img, user_message)
            messages.append(img_message)
        except NotImplementedError:
            rprint(f'[red]模型 {llm.model_name} 不支持图片上传[/red]')
            sys.exit()

    messages.append(user_message)

    if args.log:
        from utils.context import print_messages
        print_messages(messages)

    return messages


def output_parse(args: Namespace, llm: BaseLLM, messages: list[dict]):
    stream = False
    if args.stream:
        stream = True

    buffer = ''

    if stream:
        response = llm.stream_message(messages)
        for block in response:
            buffer += block
            sys.stdout.write(block)
            sys.stdout.flush()
    else:
        response = llm.message(messages)
        buffer += response
        if args.markdown:
            print_markdown(response)
        else:
            sys.stdout.write(response)
            sys.stdout.flush()

    if args.copy:
        import pyperclip
        pyperclip.copy(buffer)
    if args.output:
        from utils.context import save_output
        save_output(buffer)

    return buffer


def main() -> None:
    from parse import init_parse
    args = init_parse()

    # 命令式参数
    setting_args_parse(args)

    # 模型参数
    llm = config_model(args)

    # 输入参数
    messages = input_args_parse(args, llm)

    # 输出参数
    response = output_parse(args, llm, messages)

    # 历史对话保存
    from utils.context import save_previous
    save_previous(messages, response)

if __name__ == '__main__':
    main()