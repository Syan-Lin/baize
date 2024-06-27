from typing import Generator
from llm.base_llm import BaseLLM
from zhipuai import ZhipuAI
from pathlib import Path


class GLM(BaseLLM):
    def __init__(self, model_name: str, model_config: dict):
        super().__init__(model_name, model_config)
        self.init()


    def init(self):
        api_key = self.model_config.get("api_key")
        if api_key is None:
            raise ValueError("GLM 需要配置 API key")
        self.client = ZhipuAI(api_key=api_key)


    def message(self, message: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            temperature=self.model_config.get("temperature"),
            top_p=self.model_config.get("top_p"),
        )
        return response.choices[0].message.content


    def stream_message(self, message: list[dict]) -> Generator:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            temperature=self.model_config.get("temperature"),
            top_p=self.model_config.get("top_p"),
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


    def upload_file(self, file_path: list | str, message: dict) -> list[dict]:
        return super().upload_file(file_path, message)


    def upload_img(self, img_path: list | str, message: dict) -> list[dict]:
        if self.model_name != 'glm-4v':
            return super().upload_img(img_path, message)

        if isinstance(img_path, str):
            img_path = [img_path]
        if len(img_path) > 1:
            raise ValueError("glm-4v 不支持多张图片")

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
                    'url': img.decode('utf-8')
                }
            })
        return [img_message]


    def call_tool(self, tools: dict, message: list[dict]) -> tuple[str, str, dict, dict]:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=message,
            temperature=self.model_config.get("temperature"),
            top_p=self.model_config.get("top_p"),
            tools=tools,
        )
        response = response.choices[0].message
        response_message, function_name, args, tool_message = None, None, None, None

        if response.tool_calls is not None:
            function_name = response.tool_calls[0].function.name
            args = response.tool_calls[0].function.arguments
            tool_message = response.model_dump()
        else:
            response_message = response.content
        return response_message, function_name, args, tool_message