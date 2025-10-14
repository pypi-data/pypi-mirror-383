import base64
import os
from itertools import tee
from pathlib import Path

from openai import OpenAI, NOT_GIVEN


_mime_types = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".tiff": "image/tiff",
}

_ocr_prompt = """
Extract content from image.

Your answer should be a json, containing abstract and full text in such struct: `{"abstract": "xxxx", "full": "xxxx"}`.

The full text should be in markdown syntax. It may has lists, tables, code.

If something looks like list in full text, represent it with legal markdown list syntax.
""".strip()


class Client:
    def __init__(self, name: str, base_url: str, model: str, api_key: str, tools):
        self.name = name
        self.model = model
        self.tools = tools
        self._client = OpenAI(base_url=base_url, api_key=api_key)

    def stream_response(self, messages: list[dict], json: bool = False):
        response_format = {"type": "json_object"} if json else NOT_GIVEN
        tools = self.tools if self.tools else NOT_GIVEN
        stream = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            response_format=response_format,
            stream=True,
            stream_options={"include_usage": True},
        )

        stream1, stream2 = tee(stream)
        stream3, stream4 = tee(stream2)

        return (
            (
                chunk.choices[0].delta.content
                for chunk in stream1
                if chunk.choices and chunk.choices[0].delta.content
            ),
            (
                chunk.choices[0].delta.tool_calls
                for chunk in stream3
                if chunk.choices and chunk.choices[0].delta.tool_calls
            ),
            (
                chunk.usage
                for chunk in stream4
                if chunk.usage is not None
                and chunk.usage.total_tokens is not None
                and chunk.usage.total_tokens > 0
            ),
        )

    def oneshot(self, uri, prompt) -> str:
        if prompt is not None and os.path.exists(prompt):
            with open(prompt, "r", encoding="utf-8") as prompt_file:
                prompt = prompt_file.read()

        user_msg = None
        if os.path.exists(uri):
            if os.path.splitext(uri)[1].lower() in {".txt", ".csv", ".json", ".md"}:
                with open(uri, "r", encoding="utf-8") as text_file:
                    user_msg = text_file.read()
            else:
                with open(uri, "rb") as image_file:
                    base64_data = base64.b64encode(image_file.read()).decode("utf-8")
                    mime_type = _mime_types.get(Path(uri).suffix.lower(), "image/jpeg")
                    b64 = f"data:{mime_type};base64,{base64_data}"
                    user_msg = [{"type": "image_url", "image_url": {"url": b64}}]
                    if prompt is None:
                        prompt = _ocr_prompt
        else:
            user_msg = uri

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_msg},
        ]

        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
        )

        return response.choices[0].message.content
