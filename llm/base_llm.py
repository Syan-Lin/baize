from abc import ABC, abstractmethod
from utils.log import log

class BaseLLM(ABC):
    def __init__(self, model_name: str, model_config: dict):
        self.model_name = model_name
        self.model_config = model_config


    @abstractmethod
    def init(self):
        raise NotImplementedError


    @abstractmethod
    def message(self, message: list[dict]) -> str:
        raise NotImplementedError


    @abstractmethod
    def stream_message(self, message: list[dict]) -> str:
        raise NotImplementedError


    @abstractmethod
    def upload_file(self, file_path: list | str, message: dict) -> list[dict]:
        if isinstance(file_path, str):
            file_path = [file_path]

        from utils.file import parse_file
        files = parse_file(file_path)

        messages = []
        for file in files:
            messages.append({'role': 'system', 'content': f'{file}'})
        messages.append(message)

        return messages


    @abstractmethod
    def upload_img(self, img_path: list | str, message: dict) -> list[dict]:
        raise NotImplementedError(f'{self.model_name} 不支持图片上传')


    @abstractmethod
    def call_tool(self, tools: dict, message: list[dict]) -> tuple[str, str, dict, dict]:
        raise NotImplementedError(f'{self.model_name} 不支持 function call')


@log
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