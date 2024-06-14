from typing import Generator
from llm.base_llm import BaseLLM
from openai import OpenAI

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

    def stream_message(self, message: str) -> Generator:
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