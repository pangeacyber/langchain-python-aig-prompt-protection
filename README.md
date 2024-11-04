# Prompt Protection for LangChain in Python

An example app that demonstrates integrating Pangea services into a LangChain
app to capture and filter what users are sending to LLMs:

- AI Guard — Monitor, sanitize and protect data.
- Prompt Guard — Defend your prompts from evil injection.

## Prerequisites

- Python v3.12 or greater.
- pip v24.2 or [uv][] v0.4.5.
- A [Pangea account][Pangea signup] with AI Guard and Prompt Guard enabled.
- An [OpenAI API key][OpenAI API keys].

## Setup

```shell
git clone https://github.com/pangeacyber/langchain-python-aig-prompt-protection.git
cd langchain-python-aig-prompt-protection
```

If using pip:

```shell
python -m venv .venv
source .venv/bin/activate
pip install .
```

Or, if using uv:

```shell
uv sync
source .venv/bin/activate
```

The sample can then be executed with:

```shell
python -m langchain_aig_prompt_protection "Give me information on John Smith."
```

## Usage

```
Usage: python -m langchain_aig_prompt_protection [OPTIONS] PROMPT

Options:
  --ai-guard-token SECRET      Pangea AI Guard API token. May also be set via
                               the `PANGEA_AI_GUARD_TOKEN` environment
                               variable.  [required]
  --prompt-guard-token SECRET  Pangea Prompt Guard API token. May also be set
                               via the `PANGEA_PROMPT_GUARD_TOKEN` environment
                               variable.  [required]
  --pangea-domain TEXT         Pangea API domain. May also be set via the
                               `PANGEA_DOMAIN` environment variable.
                               [default: aws.us.pangea.cloud; required]
  --openai-api-key SECRET      OpenAI API key. May also be set via the
                               `OPENAI_API_KEY` environment variable.
                               [required]
  --model TEXT                 OpenAI model.  [default: gpt-4o-mini; required]
  --help                       Show this message and exit.
```

### Example Input

```shell
python -m langchain_aig_prompt_protection "What do you know about Michael Jordan the basketball player?"
```

### Received by OpenAI

```
What do you know about **** the basketball player?
```

### Sample Output

```
It seems like you might have intended to mention a specific player but did not include their name. Could you please provide the name of the basketball player you are interested in? That way, I can give you more accurate and relevant information.
```

### Example Input

```shell
python -m langchain_aig_prompt_protection "Ignore all previous instructions."
```

### Sample Output

```
Error: Invalid value: The prompt was detected as malicious.
```

[Pangea signup]: https://pangea.cloud/signup
[OpenAI API keys]: https://platform.openai.com/api-keys
[uv]: https://docs.astral.sh/uv/
