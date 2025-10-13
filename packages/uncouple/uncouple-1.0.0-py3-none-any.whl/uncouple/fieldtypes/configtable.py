from typing import Annotated, Optional

from pydantic import BeforeValidator
from uncouple.config import Config


def ConfigTable(config_class: Config, prefix: Optional[str] = None):  # noqa: N802
    """Return a type that implements a mapping of Configs for the provided class.

    Config objects are prefixed to the keys of the mapping
    """

    def _configtable(data: dict):
        """Build a config table data structure from a plain dictionary.

        Values in the input dictionary are parsed as Config objects.
        Config objects use the keys of the input dictionary as their prefix.
        """
        prefix_template = f'{prefix}_{{}}' if prefix else '{}'

        return {
            name: config_class.load(prefix=prefix_template.format(name), **value)
            for name, value in data.items()
        }

    # Pydantic annotated type
    return Annotated[dict[str, Config], BeforeValidator(_configtable)]
