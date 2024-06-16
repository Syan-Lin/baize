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
    elif model_name in models['glm']['models']:
        from llm.glm import GLM
        llm = GLM(model_name, model_config)
    elif model_name in models['deepseek']['models']:
        from llm.deepseek import DeepSeek
        llm = DeepSeek(model_name, model_config)
    elif model_name in models['doubao']['models']:
        from llm.doubao import DouBao
        llm = DouBao(model_name, model_config)
    else:
        rprint(f'[red]不支持模型 {model_name}[/red]')
        sys.exit()

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
    elif args.createtemplate:
        from utils.templates import create_template
        create_template()
        sys.exit()
    elif args.deletetemplate:
        from utils.templates import delete_template
        delete_template(args.deletetemplate)
        sys.exit()
    elif args.showtemplate:
        from utils.templates import get_template
        template = get_template(args.showtemplate[0])
        print_markdown(template)
        sys.exit()


def input_args_parse(args: Namespace, llm: BaseLLM) -> list[dict]:
    # Prompt 输入
    if args.paste:
        import pyperclip
        input_prompt = [pyperclip.paste()]
    else:
        if args.prompt:
            input_prompt = args.prompt
        else:
            input_prompt = [sys.stdin.read()]

    messages = []

    # 历史对话引入
    if args.previous:
        from utils.context import load_previous
        history = load_previous()
        if len(history) > 0:
            messages += history
    else:
        # Context 引入
        from utils.context import load_context
        context = load_context()
        if context != '':
            messages.append({'role': 'system', 'content': context})

    # 构造模板
    template = None
    if args.templates:
        from utils.templates import get_template
        template = get_template(args.templates[0])

    if template is None:
        user_message = {'role': 'user', 'content': input_prompt[0]}
    else:
        if '{}' not in template:
            template_format = template + '\n' + input_prompt[0]
        else:
            format_num = template.count('{}')
            if len(input_prompt) != format_num:
                rprint(f'[red]输入参数数量与模板不一致， Prompt 模板中有 [green]{format_num}[/green] 个参数，而给了 [green]{len(input_prompt)}[/green] 个参数[/red]')
                sys.exit()
            template_format = template.format(*input_prompt)
        user_message = {'role': 'user', 'content': template_format}

    # 文件引入
    if args.file:
        try:
            file_message = llm.upload_file(args.file, user_message)
            messages += file_message
        except NotImplementedError:
            rprint(f'[red]模型 {llm.model_name} 不支持文件上传[/red]')
            sys.exit()
    if args.img:
        try:
            img_message = llm.upload_img(args.img, user_message)
            messages += img_message
        except NotImplementedError:
            rprint(f'[red]模型 {llm.model_name} 不支持图片上传[/red]')
            sys.exit()

    if not args.file and not args.img:
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
        sys.stdout.write('\n')
    else:
        response = llm.message(messages)
        buffer += response
        if args.markdown:
            print_markdown(response + '\n')
        else:
            sys.stdout.write(response + '\n')
            sys.stdout.flush()

    if args.copy:
        import pyperclip
        pyperclip.copy(buffer)
    if args.output:
        save_path = args.output[0]
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(buffer)

    return buffer


def main() -> None:
    from parse import init_parse
    args = init_parse()

    # 命令式参数
    setting_args_parse(args)

    # 模型参数
    llm = config_model(args)

    if args.cli or args.clidetail:
        # 命令行模式
        from cli.cli import cli_main
        cli_main(args, llm)
    elif args.workflow:
        # 工作流模式
        pass
    else:
        # 输入参数
        messages = input_args_parse(args, llm)

        # 输出参数
        response = output_parse(args, llm, messages)

        # 历史对话保存
        from utils.context import save_previous
        save_previous(messages, response)

if __name__ == '__main__':
    main()