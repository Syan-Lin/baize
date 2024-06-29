from typing import Generator
from llm.base_llm import BaseLLM
from ollama import Client, Options

class Ollama(BaseLLM):
    def __init__(self, model_name: str, model_config: dict):
        super().__init__(model_name, model_config)
        self.options = Options(
            temperature=model_config.get("temperature"),
            top_p=model_config.get("top_p"),
            frequency_penalty=model_config.get("frequency_penalty"),
            presence_penalty=model_config.get("presence_penalty"),
        )
        self.model_name = model_config['checkpoint']
        self.init()


    def init(self):
        base_url = self.model_config.get("base_url")
        if base_url is None:
            base_url = '127.0.0.1:11434'
        self.client = Client(host=base_url)


    def message(self, message: list[dict]) -> str:
        response = self.client.chat(
            model=self.model_name,
            messages=message,
            options=self.options,
        )
        return response['message']['content']


    def stream_message(self, message: str) -> Generator:
        response = self.client.chat(
            model=self.model_name,
            messages=message,
            options=self.options,
            stream=True,
        )
        for chunk in response:
            yield chunk['message']['content']


    def upload_file(self, file_path: list | str, message: dict) -> dict:
        return super().upload_file(file_path, message)


    def upload_img(self, img_path: list | str, message: dict) -> dict:
        return super().upload_img(img_path, message)


    def call_tool(self, tools: dict, message: list[dict]) -> tuple[str, str, dict, dict]:
        return super().call_tool(tools, message)