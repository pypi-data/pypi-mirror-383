import inspect
import os
from collections import namedtuple
from itertools import chain
from typing import Any, Generator

from decouple import config
from pydantic import BaseModel


class Config(BaseModel):
    """Extend with type annotations to load configuration from environment variables."""

    @classmethod
    def load(cls, prefix: str = '', **defaults):
        """Load configuration from environment variables."""
        loaded_items = _nested_dict(_gen_loaded_items(prefix, cls, defaults))
        return cls(**(defaults | loaded_items))

    @staticmethod
    def find():
        """Iterate all avaialble config parameters.

        Include from both environment and decouple's loaded repository.
        """
        return iter(
            {
                key: value
                for key, value in chain(
                    os.environ.items(),
                    config.config.repository.data.items(),
                )
            }
        )


def _gen_loaded_items(
    prefix: str, cls: type(Config), defaults: dict[str, Any]
) -> Generator[[str, Any], None, None]:
    """Generate loaded items from the given Config class."""
    prefix_keys = [prefix] if prefix else []

    stack_item = namedtuple('stack_item', 'keys cls')
    stack = [stack_item(keys=[], cls=cls)]

    while stack:
        item = stack.pop()
        for _param, _type in inspect.signature(item.cls).parameters.items():
            # Resolve value to:
            # 1. Envvar or .env file (via decouple)
            # 2. Otherwise, explicitly passed kwarg in load()
            # 3. Otherwise, default as configured in the Config class
            # 4. Final fallback value will be `empty` if no default was
            #    specified in 3, in which case the param is omitted
            item_keys = [*item.keys, _param]
            config_key = '_'.join((*prefix_keys, *item_keys))
            value = config(config_key, default=defaults.get(_param, _type.default))

            if value != _type.empty:
                yield item_keys, value

            if inspect.isclass(_type.annotation):
                if issubclass(_type.annotation, Config):
                    stack.append(stack_item(item_keys, _type.annotation))


def _nested_dict(pairs: list[tuple[list[str], Any]]) -> dict:
    """Build a nested dictionary from an iterable of (keys: list[str], value: Any).

    The first element of each pair is a list of keys, and the second element is
    the value.
    """
    nested = {}
    for keys, value in pairs:
        cursor = nested
        for key in keys[:-1]:
            cursor = cursor.setdefault(key, {})
        cursor[keys[-1]] = value
    return nested
