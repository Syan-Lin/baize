from typing import Generator
from llm.base_llm import BaseLLM
from openai import OpenAI
from pathlib import Path

class Qwen(BaseLLM):
    def __init__(self, model_name: str, model_config: dict):
        super().__init__(model_name, model_config)
        self.init()


    def init(self):
        api_key = self.model_config.get("api_key")
        base_url = self.model_config.get("base_url")
        if api_key is None:
            raise ValueError("API key is required for Qwen models.")
        elif base_url is None:
            raise ValueError("Base URL is required for Qwen models.")
        self.client = OpenAI(api_key=api_key, base_url=base_url)


    def message(self, message: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            temperature=self.model_config.get("temp"),
            top_p=self.model_config.get("top_p"),
            frequency_penalty=self.model_config.get("frequency_penalty"),
            presence_penalty=self.model_config.get("presence_penalty"),
        )
        return response.choices[0].message.content


    def stream_message(self, message: list[dict]) -> Generator:
        response = self.client.chat.completions.create(
            model=self.model_name,
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


    def upload_file(self, file_path: list | str, message: dict | None = None) -> list[dict]:
        if isinstance(file_path, str):
            file_path = [file_path]

        files = []
        for path in file_path:
            files.append(self.client.files.create(file=Path(path), purpose="file-extract"))

        file_content = ''
        for file in files:
            file_content += f'fileid://{file.id},'
        file_content = file_content[:-1]

        file_messages = []
        file_messages.append({'role': 'system', 'content': file_content})
        file_messages.append(message)

        return file_messages


    def upload_img(self, img_path: str | str, message: dict | None = None) -> list[dict]:
        return super().upload_img(img_path, message)