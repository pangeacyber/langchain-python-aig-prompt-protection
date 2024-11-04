from __future__ import annotations

from typing import Any, override

import click
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from langchain_aig_prompt_protection.runnables import PangeaAIGuard, PangeaPromptGuard
from langchain_aig_prompt_protection.runnables.prompt_guard import MaliciousPromptError


class SecretStrParamType(click.ParamType):
    name = "secret"

    @override
    def convert(self, value: Any, param: click.Parameter | None = None, ctx: click.Context | None = None) -> SecretStr:
        if isinstance(value, SecretStr):
            return value

        return SecretStr(value)


SECRET_STR = SecretStrParamType()


@click.command()
@click.option(
    "--ai-guard-token",
    envvar="PANGEA_AI_GUARD_TOKEN",
    type=SECRET_STR,
    required=True,
    help="Pangea AI Guard API token. May also be set via the `PANGEA_AI_GUARD_TOKEN` environment variable.",
)
@click.option(
    "--prompt-guard-token",
    envvar="PANGEA_PROMPT_GUARD_TOKEN",
    type=SECRET_STR,
    required=True,
    help="Pangea Prompt Guard API token. May also be set via the `PANGEA_PROMPT_GUARD_TOKEN` environment variable.",
)
@click.option(
    "--pangea-domain",
    envvar="PANGEA_DOMAIN",
    default="aws.us.pangea.cloud",
    show_default=True,
    required=True,
    help="Pangea API domain. May also be set via the `PANGEA_DOMAIN` environment variable.",
)
@click.option(
    "--openai-api-key",
    envvar="OPENAI_API_KEY",
    type=SECRET_STR,
    required=True,
    help="OpenAI API key. May also be set via the `OPENAI_API_KEY` environment variable.",
)
@click.option("--model", default="gpt-4o-mini", show_default=True, required=True, help="OpenAI model.")
@click.argument("prompt")
def main(
    *,
    prompt: str,
    ai_guard_token: SecretStr,
    prompt_guard_token: SecretStr,
    pangea_domain: str,
    openai_api_key: SecretStr,
    model: str,
) -> None:
    chain = (
        ChatPromptTemplate.from_messages([("user", "{input}")])
        | PangeaAIGuard(token=ai_guard_token, domain=pangea_domain)
        | PangeaPromptGuard(token=prompt_guard_token, domain=pangea_domain)
        | ChatOpenAI(model=model, api_key=openai_api_key)
        | StrOutputParser()
    )

    try:
        click.echo(chain.invoke({"input": prompt}))
    except MaliciousPromptError:
        raise click.BadParameter("The prompt was detected as malicious.")


if __name__ == "__main__":
    main()
