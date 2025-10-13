# uncouple

`uncouple` provides a Pydantic-based interface on top of [python-decouple](https://pypi.org/project/python-decouple/) for managing configurations, incuding out of the box support for parsing network addresses, YAML data and more.


## Installation

Install `uncouple` using uv:

```bash
uv add uncouple
```

Or using pip:

```bash
pip install uncouple
```

## Synopsis

```python
from uncouple import Config, StringList, Addr, YarlUrl
from pathlib import Path


class OptionsConfig(Config):
    TIMEOUT: int
    WHITELIST: StringList
    LOG_PATH: Path


class AppConfig(Config):
    NAME: str = 'my-default-name'
    REMOTE_ADDR: Addr
    API_URL: YarlUrl
    OPTIONS: OptionsConfig


# With environment as:
#
# APP_REMOTE_ADDR=localhost:1234
# APP_API_URL=http://api.example.com:1234/foo
# APP_OPTIONS_TIMEOUT=60
# APP_OPTIONS_WHITELIST=john,paul,george,ringo
# APP_OPTIONS_LOG_PATH=/var/logs/app
#
config = AppConfig.load(prefix='APP')

# Accessing configuration values
config.NAME  # 'my-default-name', from default
config.REMOTE_ADDR  # Addr(host='localhost', port=1234)
config.API_URL  # yarl.URL('http://api.example.com:1234/foo')
config.OPTIONS.TIMEOUT  # 60
config.OPTIONS.WHITELIST  # ['john', 'paul', 'george', 'ringo']
config.OPTIONS.LOG_PATH  # Path('/var/logs/app')
```

## Contributing

Contributions to `uncouple` are welcome! Please follow the standard GitHub pull request workflow. Make sure to add unit tests for any new or changed functionality and ensure your code passes existing tests.

For bug reports, feature requests, or general inquiries, please open an issue.

---

This template provides a foundation for the README. Depending on the package's complexity and additional functionalities not covered in the snippet, you might need to expand on certain sections or add new ones, such as "Advanced Usage", "API Reference", or "Troubleshooting".