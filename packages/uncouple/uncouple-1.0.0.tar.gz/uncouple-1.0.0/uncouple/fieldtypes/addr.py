from dataclasses import dataclass
from typing import Annotated

from pydantic import BeforeValidator


# Network address (host, port)
@dataclass
class AddrStruct:
    """Network Address structure and type annotation."""

    host: str
    port: int

    @classmethod
    def from_string(cls, value: str) -> 'Addr':
        """Parse a string into an AddrStruct."""
        if value is None:
            return None

        host, port = value.split(':')
        return cls(host, int(port))

    def __eq__(self, other):
        return (self.host, self.port) == tuple(other)

    def __tuple__(self):
        return (self.host, self.port)


Addr = Annotated[AddrStruct, BeforeValidator(AddrStruct.from_string)]
