from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
import yaml
import yarl
from uncouple import Addr, Config, ConfigTable, ReadYaml, StringList, YarlUrl


def test_app_config_loading(monkeypatch):
    monkeypatch.setenv('APP_NAME', 'myapp')
    monkeypatch.setenv('APP_REMOTE_ADDR', 'localhost:1234')
    monkeypatch.setenv('APP_API_URL', 'http://api.example.com:1234/foo')
    monkeypatch.setenv('APP_OPTIONS_TIMEOUT', '60')
    monkeypatch.setenv('APP_OPTIONS_WHITELIST', 'john,paul,george,ringo')
    monkeypatch.setenv('APP_OPTIONS_LOG_PATH', '/var/logs/app')

    class OptionsConfig(Config):
        TIMEOUT: int
        WHITELIST: StringList
        LOG_PATH: Path

    class AppConfig(Config):
        NAME: str
        REMOTE_ADDR: Addr
        API_URL: YarlUrl
        OPTIONS: OptionsConfig

    config = AppConfig.load(prefix='APP')

    # Assertions to verify that the configuration is loaded correctly
    assert config.NAME == 'myapp'
    assert config.REMOTE_ADDR.host == 'localhost'
    assert config.REMOTE_ADDR.port == 1234
    assert config.API_URL == yarl.URL('http://api.example.com:1234/foo')
    assert config.OPTIONS.TIMEOUT == 60
    assert config.OPTIONS.WHITELIST == ['john', 'paul', 'george', 'ringo']
    assert config.OPTIONS.LOG_PATH == Path('/var/logs/app')


def test_config(monkeypatch):
    class TestConfig(Config):
        STRING: str
        INT: int
        ADDR: Addr
        YAML: ReadYaml
        DEFAULTED: str = 'default'

    with monkeypatch.context() as m:
        m.setenv('FOO_STRING', 'one')
        m.setenv('FOO_INT', '1')
        m.setenv('FOO_ADDR', 'host:1234')

        with NamedTemporaryFile() as tmp:
            yaml_data = {'foo': 'foostring', 'bar': ['bar1', 'bar2']}
            tmp.write(bytes(yaml.dump(yaml_data), 'utf8'))
            tmp.file.flush()
            m.setenv('FOO_YAML', tmp.name)

            config = TestConfig.load('FOO')

        assert config.STRING == 'one'
        assert config.INT == 1
        assert config.ADDR == ('host', 1234)
        assert config.DEFAULTED == 'default'
        assert config.YAML.yaml == yaml_data


def test_configtable(monkeypatch):
    class MyConfig(Config):
        FOO: str = 'default_foo'
        BAR: str = 'default_bar'

    class TestConfig(Config):
        MYTABLE: ConfigTable(MyConfig)  # type: ignore

    with monkeypatch.context() as m:
        m.setenv('A_FOO', 'env_foo')
        m.setenv('B_BAR', 'env_bar')

        config = TestConfig.load(
            **{
                'MYTABLE': {
                    'A': {'BAR': 'read_bar'},
                    'B': {'FOO': 'read_foo'},
                    'C': {},
                }
            }
        )

        assert config.MYTABLE['A'].FOO == 'env_foo'
        assert config.MYTABLE['A'].BAR == 'read_bar'

        assert config.MYTABLE['B'].FOO == 'read_foo'
        assert config.MYTABLE['B'].BAR == 'env_bar'

        assert config.MYTABLE['C'].FOO == 'default_foo'
        assert config.MYTABLE['C'].BAR == 'default_bar'


def test_yaml():
    class TestConfig(Config):
        YAMLONE: ReadYaml
        YAMLTWO: ReadYaml

    with NamedTemporaryFile() as tmp_one, NamedTemporaryFile() as tmp_two:
        tmp_one.write(bytes('{ foo: foo_one }', 'utf8'))
        tmp_one.file.flush()

        tmp_two.write(bytes('{ foo: foo_two }', 'utf8'))
        tmp_two.file.flush()

        config = TestConfig.load(**{'YAMLONE': tmp_one.name, 'YAMLTWO': tmp_two.name})

    assert config.YAMLONE.yaml['foo'] == 'foo_one'
    assert config.YAMLTWO.yaml['foo'] == 'foo_two'


############################
# Test booleans
############################
@pytest.mark.parametrize(
    'strvalue',
    ['true', 'True', 'TRUE', 'yes', 'Yes', 'YES', 'on', 'On', 'ON', '1', 't', 'T'],
)
def test_bool_trues(monkeypatch, strvalue: str):
    _test_bool(monkeypatch, strvalue, True)


@pytest.mark.parametrize(
    'strvalue',
    ['false', 'False', 'FALSE', 'no', 'No', 'NO', 'off', 'Off', 'OFF', '0', 'f', 'F'],
)
def test_bool_falses(monkeypatch, strvalue: str):
    _test_bool(monkeypatch, strvalue, False)


def _test_bool(monkeypatch, strvalue: str, expected: bool):
    class TestConfig(Config):
        BOOL: bool

    with monkeypatch.context() as m:
        m.setenv('FOO_BOOL', strvalue)
        config = TestConfig.load('FOO')

    assert config.BOOL is expected
