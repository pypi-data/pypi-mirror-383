from pathlib import Path
from typing import Annotated, Generic, TypeVar, Union

import yaml
from pydantic import AfterValidator, BaseModel, BeforeValidator

T = TypeVar('T')


class LoadedData(BaseModel, Generic[T]):
    """Dictionary-like data loaded from a path."""

    path: Path
    yaml: T


class Loader:
    """Loader for YAML files."""

    path: Path

    def read_yaml(self, value: Union[str, Path]) -> 'LoadedData[T]':
        """Read YAML file and return its content."""
        self.path = Path(value)
        return yaml.safe_load(self.path.read_text())

    def wrap_data(self, data: T):
        """Wrap data into a LoadedData object."""
        return LoadedData(
            path=self.path,
            yaml=data,
        )


loader = Loader()

ReadYaml = Annotated[
    T, BeforeValidator(loader.read_yaml), AfterValidator(loader.wrap_data)
]
