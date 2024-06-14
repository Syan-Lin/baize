from abc import ABC, abstractmethod

openai_models   = ['gpt-4o', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']
qwen_models     = ['qwen-max', 'qwen-long', 'qwen-turbo', 'qwen-plus']
deepseek_models = ['deepseek-chat', 'deepseek-coder']
zhipu_models    = ['glm-4', 'glm-4v', 'glm-3-turbo']

class BaseLLM(ABC):
    def __init__(self, model_name: str, model_config: dict):
        self.model_name = model_name
        self.model_config = model_config

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def message(self, message: str) -> str:
        pass

    @abstractmethod
    def stream_message(self, message: str) -> str:
        pass