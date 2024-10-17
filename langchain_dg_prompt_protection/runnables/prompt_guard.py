from __future__ import annotations

from typing import Any, override

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import RunnableConfig, RunnableSerializable
from pangea import PangeaConfig
from pangea.services import PromptGuard
from pangea.services.prompt_guard import Message
from pydantic import SecretStr
from pydantic_core import to_json

__all__ = ["MaliciousPromptError", "PangeaPromptGuard"]


def _format_content(content: str | list[str | dict]) -> str:
    if isinstance(content, list):
        return "".join([block for block in content if not isinstance(block, dict)])

    return content


def _convert_message(message: BaseMessage) -> Message:
    content = _format_content(message.content)
    role = None

    if isinstance(message, ChatMessage):
        role = message.role
    elif isinstance(message, HumanMessage):
        role = "user"
    elif isinstance(message, AIMessage):
        role = "assistant"
    elif isinstance(message, SystemMessage):
        role = "system"
    elif isinstance(message, FunctionMessage):
        role = "function"
    elif isinstance(message, ToolMessage):
        role = "tool"
    else:
        raise TypeError(f"Received unknown message type {message}.")

    return Message(content=content, role=role)


class MaliciousPromptError(RuntimeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class PangeaPromptGuard(RunnableSerializable[PromptValue, PromptValue]):
    """
    Runnable that uses Pangea's Prompt Guard service to defend against prompt
    injection.
    """

    _client: PromptGuard

    def __init__(self, *, token: SecretStr, domain: str = "aws.us.pangea.cloud", threshold: int = 70) -> None:
        """
        Args:
            token: Pangea Prompt Guard API token.
            domain: Pangea API domain.
        """

        super().__init__()
        self._client = PromptGuard(token=token.get_secret_value(), config=PangeaConfig(domain=domain))

    @override
    def invoke(self, input: PromptValue, config: RunnableConfig | None = None, **kwargs: Any) -> PromptValue:
        response = self._client.guard([_convert_message(message) for message in input.to_messages()])
        assert response.result
        if response.result.prompt_injection_detected:
            raise MaliciousPromptError(to_json(response.result).decode("utf-8"))

        return input
