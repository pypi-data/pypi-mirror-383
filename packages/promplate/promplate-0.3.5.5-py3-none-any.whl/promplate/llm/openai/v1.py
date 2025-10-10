from contextlib import suppress
from copy import copy
from functools import cached_property
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Callable, ParamSpec, TypeVar

from openai import AsyncClient, Client

from ...prompt.chat import Message, ensure
from ...prompt.utils import _get_aclient, _get_client, get_user_agent
from ..base import *

P = ParamSpec("P")
T = TypeVar("T")


class Config(Configurable):
    def __init__(self, **config):
        super().__init__(**config)
        self._run_config = {}

    def bind(self, **run_config):
        obj = copy(self)
        obj._run_config = self._run_config | run_config
        return obj

    @cached_property
    def _user_agent(self):
        from openai.version import VERSION

        return get_user_agent(self, ("OpenAI", VERSION))

    @property
    def _config(self):  # type: ignore
        ua_header = {"User-Agent": self._user_agent}
        config = dict(super()._config)
        config["default_headers"] = config.get("default_headers", {}) | ua_header
        return MappingProxyType(config)

    @cached_property
    def _client(self):
        if "http_client" in self._config:
            return Client(**self._config)
        else:
            return Client(**self._config, http_client=_get_client())

    @cached_property
    def _aclient(self):
        if "http_client" in self._config:
            return AsyncClient(**self._config)
        else:
            return AsyncClient(**self._config, http_client=_get_aclient())


if TYPE_CHECKING:

    def same_params_as(_: Callable[P, Any]) -> Callable[[Callable[..., None]], Callable[P, None]]: ...

    class ClientConfig(Config):
        @same_params_as(Client)
        def __init__(self, **config): ...

    class AsyncClientConfig(Config):
        @same_params_as(AsyncClient)
        def __init__(self, **config): ...

else:
    ClientConfig = AsyncClientConfig = Config


class TextComplete(ClientConfig):
    def __call__(self, text: str, /, **config):
        config = self._run_config | config | {"prompt": text}
        result = self._client.completions.create(**config, stream=False)
        return result.choices[0].text


class AsyncTextComplete(AsyncClientConfig):
    async def __call__(self, text: str, /, **config):
        config = self._run_config | config | {"prompt": text}
        result = await self._aclient.completions.create(**config, stream=False)
        return result.choices[0].text


class TextGenerate(ClientConfig):
    def __call__(self, text: str, /, **config):
        config = self._run_config | config | {"prompt": text}
        stream = self._client.completions.create(**config, stream=True)
        for event in stream:
            with suppress(AttributeError, IndexError):
                yield event.choices[0].text


class AsyncTextGenerate(AsyncClientConfig):
    async def __call__(self, text: str, /, **config):
        config = self._run_config | config | {"prompt": text}
        stream = await self._aclient.completions.create(**config, stream=True)
        async for event in stream:
            with suppress(AttributeError, IndexError):
                yield event.choices[0].text


class ChatComplete(ClientConfig):
    def __call__(self, messages: list[Message] | str, /, **config):
        messages = ensure(messages)
        config = self._run_config | config | {"messages": messages}
        result = self._client.chat.completions.create(**config, stream=False)
        return result.choices[0].message.content or ""


class AsyncChatComplete(AsyncClientConfig):
    async def __call__(self, messages: list[Message] | str, /, **config):
        messages = ensure(messages)
        config = self._run_config | config | {"messages": messages}
        result = await self._aclient.chat.completions.create(**config, stream=False)
        return result.choices[0].message.content or ""


class ChatGenerate(ClientConfig):
    def __call__(self, messages: list[Message] | str, /, **config):
        messages = ensure(messages)
        config = self._run_config | config | {"messages": messages}
        stream = self._client.chat.completions.create(**config, stream=True)
        for event in stream:
            with suppress(AttributeError, IndexError):
                yield event.choices[0].delta.content or ""


class AsyncChatGenerate(AsyncClientConfig):
    async def __call__(self, messages: list[Message] | str, /, **config):
        messages = ensure(messages)
        config = self._run_config | config | {"messages": messages}
        stream = await self._aclient.chat.completions.create(**config, stream=True)
        async for event in stream:
            with suppress(AttributeError, IndexError):
                yield event.choices[0].delta.content or ""


class SyncTextOpenAI(ClientConfig, LLM):
    complete = TextComplete.__call__
    generate = TextGenerate.__call__


class AsyncTextOpenAI(AsyncClientConfig, LLM):
    complete = AsyncTextComplete.__call__
    generate = AsyncTextGenerate.__call__


class SyncChatOpenAI(ClientConfig, LLM):
    complete = ChatComplete.__call__
    generate = ChatGenerate.__call__


class AsyncChatOpenAI(AsyncClientConfig, LLM):
    complete = AsyncChatComplete.__call__
    generate = AsyncChatGenerate.__call__


__all__ = (
    "TextComplete",
    "AsyncTextComplete",
    "TextGenerate",
    "AsyncTextGenerate",
    "ChatComplete",
    "AsyncChatComplete",
    "ChatGenerate",
    "AsyncChatGenerate",
    "SyncTextOpenAI",
    "AsyncTextOpenAI",
    "SyncChatOpenAI",
    "AsyncChatOpenAI",
)
