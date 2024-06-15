import sys
import os

from llm.base_llm import BaseLLM
from utils.config import models_info

def get_llm(model_name: str, model_config: dict) -> BaseLLM:
    models = models_info()
    if model_name in models['qwen']['models']:
        from llm.qwen import Qwen
        llm = Qwen(model_name, model_config)
    elif model_name in models['openai']['models']:
        from llm.openai import OpenAI
        llm = OpenAI(model_name, model_config)

    return llm

def main() -> None:
    from parse import init_parse
    args = init_parse()

    if args.setup:
        from utils.setup import setup
        setup()
        sys.exit()
    elif args.modellist:
        print('modellist')
        sys.exit()
    elif args.list:
        print('list')
        sys.exit()
    elif args.context:
        print('context')
        sys.exit()

    if args.prompt:
        input_prompt = args.prompt
    else:
        input_prompt = [sys.stdin.read()]

    # print(args)
    print(input_prompt[0])

    output_prompt = input_prompt[0]

    sys.stdout.write(output_prompt)

if __name__ == '__main__':
    main()