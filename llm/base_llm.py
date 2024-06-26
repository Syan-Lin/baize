from abc import ABC, abstractmethod

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