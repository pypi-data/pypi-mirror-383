from typing import Dict, Optional, Literal, List, Union
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from .SubstitutionDict import SubstitutionDict
from .Contents import Content, RefusalContent, TextContent
from .ToolCall import ToolCall, get_tool_call_from_dict


class Message:
    """Abstract base class for different types of messages."""

    def __init__(
        self,
        role: str,
        content: Optional[List[Content]] = None,
        name: Optional[str] = None,
    ):
        if role not in {"user", "system", "assistant", "developer", "tool"}:
            raise ValueError(
                f"Invalid role: {role}, must be one of 'user', 'system', 'assistant', 'developer', or 'tool'"
            )
        if content is not None and not isinstance(content, list):
            raise ValueError("Content must be a list")
        if name is not None and not isinstance(name, str):
            raise ValueError("name must be a string")
        self._role = role
        self._name = name
        self._content = content

    @property
    def role(self) -> str:
        return self._role

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def content(self) -> Optional[List[Content]]:
        return self._content

    def to_dict(
        self, substitution_dict: Optional[SubstitutionDict] = SubstitutionDict()
    ) -> Dict:
        """
        Convert the message object to a dictionary format.

        Args:
            substitution_dict (Optional[SubstitutionDict], optional): A dictionary for substituting values
            within the message content. Defaults to SubstitutionDict().

        Returns:
            Dict: The dictionary representation of the message.
        """
        raise NotImplementedError

    def __len__(self) -> int:
        if self._content is None:
            return 0
        return len(self._content)

    def __getitem__(self, index: int) -> Content:
        if self._content is None:
            raise ValueError("No content to get")
        return self._content[index]


class DevSysUserMessage(Message):
    """The message class for developer, system and user messages."""

    def __init__(
        self,
        role: Literal["user", "system", "developer"],
        content: Union[Content, List[Content]],
        name: Optional[str] = None,
    ):
        """
        Initialize a Message object.

        Args:
            role (Literal["user", "system", "developer"]): The role of the sender.
            content (Union[Content, List[Content]]): The content of the message.
            name (Optional[str]): The name of the sender (if applicable).

        Raises:
            ValueError: If `role` is invalid, `content` is empty, or name is not a string.
        """
        if role not in {"user", "system", "developer"}:
            raise ValueError(f"Invalid role: {role}")

        if isinstance(content, Content):
            content = [content]
        if not isinstance(content, list):
            raise ValueError("Content must be a list")
        for item in content:
            if not isinstance(item, Content):
                raise ValueError("Content items must be Content objects")
            if isinstance(item, RefusalContent):
                raise ValueError(
                    "Refusal content is not allowed in user, system, or developer messages"
                )
        if role == "system" or role == "developer":
            if len(content) != 1 or content[0].content_type != "text":
                raise ValueError(
                    "System and developer messages must have exactly one text content item"
                )

        super().__init__(role, content, name)

    def to_dict(
        self, substitution_dict: Optional[SubstitutionDict] = SubstitutionDict()
    ) -> Dict:
        message_dict = {
            "role": self._role,
            "content": [item.to_dict(substitution_dict) for item in self._content],
        }
        if self._name:
            message_dict["name"] = self._name.format_map(substitution_dict)
        return message_dict

    def __repr__(self) -> str:
        heading = f"{self._role} ({self._name}): " if self._name else f"{self._role}: "
        content = "\n".join(str(item) for item in self._content)
        content = content.replace("\n", "\n" + " " * len(heading))
        return f"\033[34m{heading}\033[0m{content}"


class AssistantMessage(Message):
    """The message class for assistant messages"""

    def __init__(
        self,
        content: Optional[Union[Content, List[Content]]] = None,
        refusal: Optional[str] = None,
        name: Optional[str] = None,
        audio: Optional[Union[Dict, str]] = None,
        tool_calls: Optional[List[ToolCall]] = None,
    ):
        """Initialize an AssistantMessage object.

        Args:
            content (Optional[Union[Content, List[Content]]], optional): The content of assistant message. Defaults to None.
            refusal (Optional[str], optional): The refusal message by the assistant. Defaults to None.
            name (Optional[str], optional): An optional name for the participant. Defaults to None.
            audio (Optional[Union[Dict, str]], optional): Data about previous audio response from the model. Defaults to None.
            tool_calls (Optional[List[ToolCall]], optional): A list of tool calls generated by the model. Defaults to None.
        """
        if tool_calls is None and content is None:
            raise ValueError("Content or tool calls must be provided")
        if content is not None:
            if isinstance(content, Content):
                content = [content]
            if not isinstance(content, list):
                raise ValueError("Content must be a list")
            for item in content:
                if not isinstance(item, TextContent) and not isinstance(
                    item, RefusalContent
                ):
                    raise ValueError(
                        "Content items must be TextContent or RefusalContent objects"
                    )

        if refusal is not None and not isinstance(refusal, str):
            raise ValueError("Refusal must be a string")
        if audio is not None:
            if not isinstance(audio, dict):
                raise ValueError("Audio must be a dictionary")
            if "id" not in audio or not isinstance(audio["id"], str):
                raise ValueError("Audio ID must be a string")
        if tool_calls is not None:
            if not isinstance(tool_calls, list):
                raise ValueError("Tool calls must be a list")
            for item in tool_calls:
                if not isinstance(item, ToolCall):
                    raise ValueError("Tool calls must be ToolCall objects")

        super().__init__("assistant", content, name)
        self._refusal = refusal
        self._audio = audio
        self._tool_calls = tool_calls

    def to_dict(self, substitution_dict=SubstitutionDict()):
        message_dict = {"role": self._role}
        if self._content:
            message_dict["content"] = [
                item.to_dict(substitution_dict) for item in self._content
            ]
        if self._name:
            message_dict["name"] = self._name.format_map(substitution_dict)
        if self._refusal:
            message_dict["refusal"] = self._refusal.format_map(substitution_dict)
        if self._audio:
            message_dict["audio"] = self._audio
        if self._tool_calls:
            message_dict["tool_calls"] = [
                item.to_dict(substitution_dict) for item in self._tool_calls
            ]
        return message_dict

    def __repr__(self) -> str:
        heading = f"{self._role} ({self._name}): " if self._name else f"{self._role}: "
        if self._content:
            content = "\n".join(str(item) for item in self._content)
        else:
            content = ""
        if self._refusal:
            content += f"\nRefusal: {self._refusal}"
        if self._audio:
            content += f"\nAudio: {self._audio['id']}"
        if self._tool_calls:
            content += "\n".join(str(item) for item in self._tool_calls)

        content = content.replace("\n", "\n" + " " * len(heading))

        return f"\033[34m{heading}\033[0m{content}"


class ToolMessage(Message):
    """The message class for tool messages"""

    def __init__(self, content: Union[Content, List[Content]], tool_call_id: str):
        """Initialize a ToolMessage object.

        Args:
            content (Union[Content, List[Content]]): The content of the message. The content must be a list of Content objects.
            tool_call_id (str): The ID of the tool call.
        """
        if isinstance(content, Content):
            content = [content]
        if not isinstance(content, list):
            raise ValueError("Content must be a list")
        for item in content:
            if not isinstance(item, Content):
                raise ValueError("Content items must be Content objects")
        if not isinstance(tool_call_id, str):
            raise ValueError("Tool call ID must be a string")
        super().__init__("tool", content=content)
        self._tool_call_id = tool_call_id

    @property
    def tool_call_id(self) -> str:
        return self._tool_call_id

    def to_dict(
        self, substitution_dict: Optional[SubstitutionDict] = SubstitutionDict()
    ) -> Dict:
        message_dict = {
            "role": self._role,
            "content": [item.to_dict(substitution_dict) for item in self._content],
            "tool_call_id": self._tool_call_id,
        }
        return message_dict

    def __repr__(self) -> str:
        heading = f"{self._role} ({self._tool_call_id}): "
        content = "\n".join(str(item) for item in self._content)
        content = content.replace("\n", "\n" + " " * len(heading))
        return f"\033[34m{heading}\033[0m{content}"


def get_assistant_message_from_response(message_dict: ChatCompletionMessage) -> Message:
    """generate a Message object from a dictionary.

    Args:
        message_dict (ChatCompletionMessage): The dictionary representation of the assistant message.

    Returns:
        Message: The AssistantMessage object.
    """
    role = message_dict.role
    if role == "assistant":
        content = message_dict.content
        content = TextContent(content) if content else None
        refusal = message_dict.refusal
        audio = message_dict.audio
        tool_calls = message_dict.tool_calls
        tool_calls = (
            [get_tool_call_from_dict(item) for item in tool_calls]
            if tool_calls
            else None
        )
        return AssistantMessage(content, refusal, None, audio, tool_calls)
    elif role == "user" or role == "system" or role == "developer":
        content = TextContent(message_dict.content)
        return DevSysUserMessage(role, content)
    else:
        raise ValueError(f"Invalid role: {role}")
