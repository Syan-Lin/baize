from typing import Generator
from llm.base_llm import BaseLLM
from volcenginesdkarkruntime import Ark
from pathlib import Path

class DouBao(BaseLLM):
    def __init__(self, model_name: str, model_config: dict):
        super().__init__(model_name, model_config)
        self.init()


    def init(self):
        api_key = self.model_config.get("api_key")
        self.endpoint_id = self.model_config.get("endpoint_id")
        if api_key is None:
            raise ValueError("DouBao 需要配置 API key")
        if self.endpoint_id is None:
            raise ValueError("DouBao 需要配置 endpoint_id")
        self.client = Ark(api_key=api_key)


    def message(self, message: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.endpoint_id,
            messages=message,
            temperature=self.model_config.get("temp"),
            top_p=self.model_config.get("top_p"),
            frequency_penalty=self.model_config.get("frequency_penalty"),
            presence_penalty=self.model_config.get("presence_penalty"),
        )
        return response.choices[0].message.content


    def stream_message(self, message: list[dict]) -> Generator:
        response = self.client.chat.completions.create(
            model=self.endpoint_id,
            messages=message,
            temperature=self.model_config.get("temp"),
            top_p=self.model_config.get("top_p"),
            frequency_penalty=self.model_config.get("frequency_penalty"),
            presence_penalty=self.model_config.get("presence_penalty"),
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


    def upload_file(self, file_path: list | str, message: dict) -> list[dict]:
        return super().upload_file(file_path, message)


    def upload_img(self, img_path: list | str, message: dict) -> list[dict]:
        return super().upload_img(img_path, message)