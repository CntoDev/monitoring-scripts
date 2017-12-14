"""Test suite for check_runner.settings"""

import pytest

from check_runner import settings


def test_unloaded_configurator():
    """Assert RunnerConfigParser raises when used without having loaded a file."""
    config_parser = settings.RunnerConfigParser()
    with pytest.raises(RuntimeError):
        config_parser.get('dummy_section', 'dummy_value')


@pytest.fixture(scope="module")
def config(tmpdir_factory):  # pylint: disable=W0621
    """Fixture that generates a usable configuration file."""
    tmpfile = tmpdir_factory.mktemp('data').join('config.ini')
    tmpfile.write(
        "[TestSection]\n"
        "key = value\n"
    )
    return tmpfile.strpath


def test_configurator_loading(config):  # pylint: disable=W0621
    """Assert RunnerConfigParser successfully loads a configuration file."""
    config_parser = settings.RunnerConfigParser()
    config_parser.read(config)


def test_configurator_fetching(config):  # pylint: disable=W0621
    """Assert RunnerConfigParser successfully fetches a given setting."""
    config_parser = settings.RunnerConfigParser()
    config_parser.read(config)
    assert config_parser.get('TestSection', 'key') == "value"
