from __future__ import annotations

import typing
import pydantic

from langbot_plugin.api.entities.builtin.platform import message as platform_message


class FunctionCall(pydantic.BaseModel):
    name: str

    arguments: str


class ToolCall(pydantic.BaseModel):
    id: str

    type: str

    function: FunctionCall


class ImageURLContentObject(pydantic.BaseModel):
    url: str

    def __str__(self):
        return self.url[:128] + ("..." if len(self.url) > 128 else "")


class ContentElement(pydantic.BaseModel):
    type: str
    """Type of the content"""

    text: typing.Optional[str] = None

    image_url: typing.Optional[ImageURLContentObject] = None

    image_base64: typing.Optional[str] = None

    file_url: typing.Optional[str] = None

    file_name: typing.Optional[str] = None

    def __str__(self):
        if self.type == "text":
            return self.text
        elif self.type == "image_url":
            return f"[Image]({self.image_url})"
        elif self.type == "file_url":
            return f"[File]({self.file_url})"
        else:
            return "Unknown content"

    @classmethod
    def from_text(cls, text: str):
        return cls(type="text", text=text)

    @classmethod
    def from_image_url(cls, image_url: str):
        return cls(type="image_url", image_url=ImageURLContentObject(url=image_url))

    @classmethod
    def from_image_base64(cls, image_base64: str):
        return cls(type="image_base64", image_base64=image_base64)

    @classmethod
    def from_file_url(cls, file_url: str, file_name: str):
        return cls(type="file_url", file_url=file_url, file_name=file_name)

class Message(pydantic.BaseModel):
    """Message for AI"""

    role: str  # user, system, assistant, tool, command, plugin
    """Role of the message"""

    name: typing.Optional[str] = None
    """Name of the message, only set when function call is returned"""

    content: typing.Optional[list[ContentElement]] | typing.Optional[str] = None
    """Content of the message"""

    tool_calls: typing.Optional[list[ToolCall]] = None
    """Tool calls"""

    tool_call_id: typing.Optional[str] = None

    def readable_str(self) -> str:
        if self.content is not None:
            return (
                str(self.role) + ": " + str(self.get_content_platform_message_chain())
            )
        elif self.tool_calls is not None:
            return f"Call tool: {self.tool_calls[0].id}"
        else:
            return "Unknown message"

    def get_content_platform_message_chain(
        self, prefix_text: str = ""
    ) -> platform_message.MessageChain | None:
        """Convert the content to a platform message MessageChain object

        Args:
            prefix_text (str): The prefix text of the first text component
        """

        if self.content is None:
            return None
        elif isinstance(self.content, str):
            return platform_message.MessageChain(
                [platform_message.Plain(text=(prefix_text + self.content))]
            )
        elif isinstance(self.content, list):
            mc: list[platform_message.MessageComponent] = []
            for ce in self.content:
                if ce.type == "text":
                    if ce.text is not None:
                        mc.append(platform_message.Plain(text=ce.text))
                elif ce.type == 'file_url':
                    if ce.file_url is not None:
                        mc.append(platform_message.File(url=ce.file_url, name=ce.file_name))
                elif ce.type == "image_url":
                    assert ce.image_url is not None
                    if ce.image_url.url.startswith("http"):
                        mc.append(platform_message.Image(url=ce.image_url.url))
                    else:  # base64
                        b64_str = ce.image_url.url

                        if b64_str.startswith("data:"):
                            b64_str = b64_str.split(",")[1]

                        mc.append(platform_message.Image(base64=b64_str))

            # find the first text component
            if prefix_text:
                for i, c in enumerate(mc):
                    if isinstance(c, platform_message.Plain):
                        mc[i] = platform_message.Plain(text=(prefix_text + c.text))
                        break
                else:
                    mc.insert(0, platform_message.Plain(text=prefix_text))

            return platform_message.MessageChain(mc)


class MessageChunk(pydantic.BaseModel):
    """消息"""

    resp_message_id: typing.Optional[str] = None
    """消息id"""

    role: str  # user, system, assistant, tool, command, plugin
    """消息的角色"""

    name: typing.Optional[str] = None
    """名称，仅函数调用返回时设置"""

    all_content: typing.Optional[str] = None
    """所有内容"""

    content: typing.Optional[list[ContentElement]] | typing.Optional[str] = None
    """内容"""

    tool_calls: typing.Optional[list[ToolCall]] = None
    """工具调用"""

    tool_call_id: typing.Optional[str] = None

    is_final: bool = False
    """是否是结束"""

    msg_sequence: int = 0
    """消息迭代次数"""

    def readable_str(self) -> str:
        if self.content is not None:
            return (
                str(self.role) + ": " + str(self.get_content_platform_message_chain())
            )
        elif self.tool_calls is not None:
            return f"调用工具: {self.tool_calls[0].id}"
        else:
            return "未知消息"

    def get_content_platform_message_chain(
        self, prefix_text: str = ""
    ) -> platform_message.MessageChain | None:
        """将内容转换为平台消息 MessageChain 对象

        Args:
            prefix_text (str): 首个文字组件的前缀文本
        """

        if self.content is None:
            return None
        elif isinstance(self.content, str):
            return platform_message.MessageChain(
                [platform_message.Plain(text=(prefix_text + self.content))]
            )
        elif isinstance(self.content, list):
            mc = []
            for ce in self.content:
                if ce.type == "text":
                    mc.append(platform_message.Plain(text=ce.text))
                elif ce.type == "file_url":
                    if ce.file_url is not None:
                        mc.append(platform_message.File(url=ce.file_url, name=ce.file_name))
                elif ce.type == "image_url":
                    if ce.image_url.url.startswith("http"):
                        mc.append(platform_message.Image(url=ce.image_url.url))
                    else:  # base64
                        b64_str = ce.image_url.url

                        if b64_str.startswith("data:"):
                            b64_str = b64_str.split(",")[1]

                        mc.append(platform_message.Image(base64=b64_str))

            # 找第一个文字组件
            if prefix_text:
                for i, c in enumerate(mc):
                    if isinstance(c, platform_message.Plain):
                        mc[i] = platform_message.Plain(text=(prefix_text + c.text))
                        break
                else:
                    mc.insert(0, platform_message.Plain(text=prefix_text))

            return platform_message.MessageChain(mc)


class ToolCallChunk(pydantic.BaseModel):
    """工具调用"""

    id: str
    """工具调用ID"""

    type: str
    """工具调用类型"""

    function: FunctionCall
    """函数调用"""
