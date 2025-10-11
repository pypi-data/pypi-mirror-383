import os
from typing import Any, Literal, NewType, TypeVar

from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.models.openai import OpenAIChat
from agno.models.together import Together

from aiwebexplorer.interfaces import IAgent

T = TypeVar("T")

ModelProvider = Literal[
    "openai",
    "togetherai",
    "deepseek",
]

ModelIdMap: NewType = dict[ModelProvider, str]

TOGETHERAI_APIKEY = "TOGETHERAI_APIKEY", "togetherai"
DEEPSEEK_APIKEY = "DEEPSEEK_APIKEY", "deepseek"
OPENAI_APIKEY = "OPENAI_APIKEY", "openai"

SupportedModelProvider = Together | DeepSeek | OpenAIChat


def _get_api_key(provider: ModelProvider | None = None) -> tuple[str, ModelProvider]:
    import dotenv

    dotenv.load_dotenv()

    # If a model provider is provided, only return the api key for that provider
    if provider:
        expected_key = f"{provider.upper()}_APIKEY"
        value = os.environ.get(expected_key)
        if value:
            return value, provider

        raise ValueError(f"Expected {expected_key} to be set when requesting provider {provider}")

    # If no provider is provided, return the api key for the first provider that is set
    for api_key, provider in [OPENAI_APIKEY, TOGETHERAI_APIKEY, DEEPSEEK_APIKEY]:
        value = os.environ.get(api_key)

        if value:
            return value, provider

    raise ValueError("No api key found for any provider")


def _get_model(
    model_id: str | None = None,
    provider: ModelProvider | None = None,
    api_key: str | None = None,
    model_id_map: ModelIdMap | None = None,
) -> SupportedModelProvider:
    if api_key is None:
        api_key, provider = _get_api_key(provider)

    if model_id is None:
        if not model_id_map:
            error_message = """
            You didn't provide a model id or a model id map. I'm expecting at least a model id map
            in order to figure it out what model to use.
            """
            raise ValueError(error_message)
        model_id = model_id_map[provider]

    if provider == "togetherai":
        return Together(id=model_id, api_key=api_key)
    elif provider == "deepseek":
        return DeepSeek(id=model_id, api_key=api_key)
    elif provider == "openai":
        return OpenAIChat(id=model_id, api_key=api_key)

    raise ValueError(f"Invalid provider: {provider}")


def get_agent(
    name: str,
    instructions: list[str],
    *,
    model_id: str | None = None,
    api_key: str | None = None,
    provider: ModelProvider | None = None,
    model_id_map: ModelIdMap | None = None,
    **kwargs: Any,
) -> IAgent[Any]:
    """Get an agent with the given name, instructions, content type, model, and other kwargs.

    See Agent constructor for Agno agent details.
    """
    model = _get_model(model_id, provider, api_key, model_id_map)
    return Agent(
        name=name,
        instructions=instructions,
        model=model,
        **kwargs,
    )
