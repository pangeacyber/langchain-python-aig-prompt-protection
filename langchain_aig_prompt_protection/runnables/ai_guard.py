from __future__ import annotations

from typing import Any, override

from langchain_core.messages import HumanMessage
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import RunnableConfig, RunnableSerializable
from pangea import PangeaConfig
from pangea.services import AIGuard
from pydantic import SecretStr

__all__ = ["PangeaAIGuard"]


class PangeaAIGuard(RunnableSerializable[PromptValue, PromptValue]):
    """
    Runnable that uses Pangea's AI Guard service to monitor, sanitize, and
    protect data.
    """

    _client: AIGuard

    def __init__(self, *, token: SecretStr, domain: str = "aws.us.pangea.cloud") -> None:
        """
        Args:
            token: Pangea AI Guard API token.
            domain: Pangea API domain.
        """

        super().__init__()
        self._client = AIGuard(token=token.get_secret_value(), config=PangeaConfig(domain=domain))

    @override
    def invoke(self, input: PromptValue, config: RunnableConfig | None = None, **kwargs: Any) -> PromptValue:
        # Retrieve latest human message.
        messages = input.to_messages()
        human_messages = [message for message in messages if isinstance(message, HumanMessage)]
        latest_human_message = human_messages[-1]
        text = latest_human_message.content
        assert isinstance(text, str)

        # Run it through AI Guard.
        guarded = self._client.guard_text(text)
        assert guarded.result

        if guarded.result.prompt_text:
            latest_human_message.content = guarded.result.prompt_text

        return input
