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
    def upload_file(self, file_path: list | str, message: dict = None) -> dict:
        raise NotImplementedError


    @abstractmethod
    def upload_img(self, img_path: list | str, message: dict = None) -> dict:
        raise NotImplementedError