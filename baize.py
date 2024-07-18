import sys
from llm.base_llm import BaseLLM
from utils.render import print_markdown, print_markdown_stream
from utils.resource import delete_resource, get_resource, print_resource_table, ResourceType
from utils.context import load_context, save_context, print_messages, load_previous, save_previous
from rich import print as rprint
from argparse import Namespace

# ======版本号====== #
___VERSION___ = '0.1'
# ================= #


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
    elif model_name in models['openai']['models']:
        from llm.openai import GPT
        llm = GPT(model_name, model_config)
    elif model_name in models['moonshot']['models']:
        from llm.moonshot import Moonshot
        llm = Moonshot(model_name, model_config)
    elif model_name in models['ollama']['models']:
        from llm.ollama import Ollama
        llm = Ollama(model_name, model_config)
    else:
        # 自定义模型默认使用 OpenAI API
        from llm.custom import CustomLLM
        llm = CustomLLM(model_name, model_config)

    return llm


def config_model(args: Namespace):
    from utils.config import model_config
    config = model_config()
    if args.model:
        config_name = args.model[0]
    else:
        if 'default_config' not in config.keys():
            rprint('[red]错误: 请先运行 `baize --setup` 配置模型[/red]')
            sys.exit()
        config_name = config['default_config']
    if config_name not in list(config.keys()):
        rprint(f'[red]错误: 未找到配置 {config_name}[/red]')
        sys.exit()
    model_name = config[config_name]['model_name']
    llm = get_llm(model_name, config[config_name])
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
    elif args.workflowlist:
        print_resource_table(ResourceType.workflow)
        sys.exit()
    elif args.toollist:
        print_resource_table(ResourceType.tool)
        sys.exit()
    elif args.set:
        from utils.config import set_default_config
        set_default_config(args.set[0])
        sys.exit()
    elif args.list:
        print_resource_table(ResourceType.templates)
        sys.exit()
    elif args.context:
        context = load_context()
        if context != '':
            print_markdown(context)
        else:
            print('Context 未设置')
        sys.exit()
    elif args.setcontext:
        save_context(args.setcontext[0])
        sys.exit()
    elif args.resetcontext:
        save_context('')
        sys.exit()
    elif args.createtemplate:
        from utils.templates import create_template
        create_template(args.createtemplate)
        sys.exit()
    elif args.deletetemplate:
        delete_resource(ResourceType.templates, args.deletetemplate)
        sys.exit()
    elif args.deletetool:
        delete_resource(ResourceType.tool, args.deletetool)
        sys.exit()
    elif args.createtool:
        from utils.tool.tool import create_tool
        create_tool()
        sys.exit()
    elif args.showtemplate:
        template = get_resource(ResourceType.templates, args.showtemplate[0])
        print_markdown(template)
        sys.exit()
    elif args.init:
        from utils.setup import init_env
        init_env(args.init[0])
        sys.exit()
    elif args.version:
        print(f'baize {___VERSION___}')
        sys.exit()
    elif args.update:
        from utils.update import update
        update()
        sys.exit()
    elif args.history:
        print_messages(load_previous())
        sys.exit()
    elif args.deletemodel:
        from utils.setup import delete_model
        delete_model(args.deletemodel)
        sys.exit()


def input_args_parse(args: Namespace, llm: BaseLLM) -> list[dict]:
    # Prompt 输入
    formatter = {
        'sysin': '',
        'paste': '',
        'input': ''
    }
    input_prompt = []
    if args.paste:
        import pyperclip
        formatter['paste'] = pyperclip.paste()
    if not sys.stdin.isatty():
        formatter['sysin'] = sys.stdin.read()
    if args.prompt:
        from utils.templates import expand_prompt
        formatter['input'] = expand_prompt(args.prompt)

    if formatter['sysin'] == '' and formatter['input'] == '' and formatter['paste'] == '':
        rprint('[red]错误: 未输入任何内容！[/red]')
        sys.exit()
    messages = []

    # 历史对话引入
    if args.previous:
        history = load_previous()
        if len(history) > 0:
            messages += history
    else:
        # Context 引入
        context = load_context()
        if context != '':
            messages.append({'role': 'system', 'content': context})

    # 构造模板
    template = None
    if args.template:
        template = get_resource(ResourceType.templates, args.template[0])

    if template is None:
        prompt = formatter['input']
        if formatter['paste'] != '':
            prompt += '\n' + formatter['paste']
        if formatter['sysin'] != '':
            prompt += '\n' + formatter['sysin']
        user_message = {'role': 'user', 'content': prompt}
    else:
        try:
            template_format = template.format(**formatter)
        except Exception as e:
            rprint(f'[red]错误: 模板解析错误\n{e}[/red]')
            sys.exit()
        user_message = {'role': 'user', 'content': template_format}

    # 文件引入
    if args.file:
        try:
            file_message = llm.upload_file(args.file, user_message)
            messages += file_message
        except NotImplementedError:
            rprint(f'[red]错误: 模型 {llm.model_name} 不支持文件上传[/red]')
            sys.exit()
    if args.img:
        try:
            img_message = llm.upload_img(args.img, user_message)
            messages += img_message
        except NotImplementedError:
            rprint(f'[red]错误: 模型 {llm.model_name} 不支持图片上传[/red]')
            sys.exit()

    if not args.file and not args.img:
        messages.append(user_message)

    if args.log:
        print_messages(messages)

    return messages


def output_parse(args: Namespace, llm: BaseLLM, messages: list[dict]):
    stream = False
    if args.stream:
        stream = True

    buffer = ''

    if stream:
        response = llm.stream_message(messages)
        if args.markdown:
            buffer = print_markdown_stream(response)
        else:
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

    if args.cli or args.clidetail or args.clikey:
        # 命令行模式
        from utils.cli.cli import cli_main
        cli_main(args, llm)
    elif args.workflow or args.showworkflow or args.createworkflow:
        # 工作流模式
        from utils.workflow.workflow import workflow_main
        workflow_main(args)
    elif args.tool:
        # 工具模式
        from utils.tool.tool import tool_main
        tool_main(args, llm)
    else:
        # 输入参数
        messages = input_args_parse(args, llm)

        # 输出参数
        response = output_parse(args, llm, messages)

        # 历史对话保存
        save_previous(messages, response)

if __name__ == '__main__':
    main()