from typing import Generator
from llm.base_llm import BaseLLM
from openai import OpenAI
from pathlib import Path

class GPT(BaseLLM):
    def __init__(self, model_name: str, model_config: dict):
        super().__init__(model_name, model_config)
        self.init()


    def init(self):
        api_key = self.model_config.get("api_key")
        base_url = self.model_config.get("base_url")
        if api_key is None:
            raise ValueError("API key is required for OpenAI models.")
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


    def upload_file(self, file_path: list | str, message: dict = None) -> dict:
        return super().upload_file(file_path, message)


    def upload_img(self, img_path: list | str, message: dict = None) -> dict:
        if self.model_name != 'gpt-4o' and self.model_name != 'gpt-4-turbo':
            return super().upload_img(img_path, message)

        if isinstance(img_path, str):
            img_path = [img_path]

        import base64
        imgs_base64 = []
        for img in img_path:
            with open(img, "rb") as f:
                imgs_base64.append(base64.b64encode(f.read()))
        img_message = {'role': 'user', 'content': []}
        img_message['content'].append({
            'type': 'text',
            'text': message['content']
        })
        for img in imgs_base64:
            img_message['content'].append({
                'type': 'image_url',
                'image_url': {
                    'url': f'data:image/jpeg;base64,{img.decode('utf-8')}'
                }
            })
        return [img_message]