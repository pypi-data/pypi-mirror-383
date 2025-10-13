from typing import Annotated, Union

from pydantic import BeforeValidator


# List of strings that will accept a single comma-separated string
# as input
def _maybe_split_str(value: Union[str, list]):
    if isinstance(value, str):
        return value.split(',')

    if isinstance(value, list):
        return value

    raise ValueError('Expected str or list of strings')


StringList = Annotated[list[str], BeforeValidator(_maybe_split_str)]
