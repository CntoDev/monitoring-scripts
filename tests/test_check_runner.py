"""Test suite for check_runner"""

# pylint: disable=E1101, W0621, R0903

import time
from unittest.mock import call

import pytest
import cachetclient.cachet

import check_runner as unit
from monitoring_scripts.nagios_common import Codes
from . import common


class CompletedProcessMock():
    """Mocks subprocess.CompletedProcess to test returncode"""

    def __init__(self, returncode):
        self.returncode = returncode


@pytest.fixture(scope='module')
def config(tmpdir_factory, base_url='http://some.url', api_key='namaste'):
    """Fixture that generates a customisable config file"""

    if base_url:
        base_url_line = 'base-url: ' + base_url + '\n'
    else:
        base_url_line = ''
    if api_key:
        api_key_line = 'api-key: ' + api_key + '\n'
    else:
        api_key_line = ''

    config_file = tmpdir_factory.mktemp('data').join('config.ini')
    config_file.write('[Cachet]\n' + base_url_line + api_key_line)

    return config_file.strpath


@pytest.mark.parametrize(
    'base_url,api_key',
    [
        (None, None),
        (None, 'baby'),
        ('donthurtme', None),
    ]
)
def test_config_params(tmpdir_factory, mocker, base_url, api_key):
    """Assert error is raised if a required parameter is missing from the config file"""

    print('base_url = %s, api_key = %s', base_url, api_key)

    config_file = config(tmpdir_factory, base_url=base_url, api_key=api_key)

    with pytest.raises(ValueError):
        unit.main(script=mocker.Mock(), component_id=99, config_file=config_file)


@pytest.mark.parametrize(
    'script_return,expected_update,n_retries',
    [
        (Codes.OK.value, Codes.OK, 0),
        (Codes.CRITICAL.value, Codes.CRITICAL, 0),
        ((Codes.CRITICAL.value, Codes.CRITICAL.value, Codes.CRITICAL.value), Codes.CRITICAL, 2),
        ((Codes.CRITICAL.value, Codes.CRITICAL.value, Codes.OK.value), Codes.OK, 2),
        ((Codes.CRITICAL.value, Codes.WARNING.value, Codes.WARNING.value), Codes.CRITICAL, 2),
        ((Codes.CRITICAL.value, Codes.WARNING.value, Codes.OK.value), Codes.OK, 2),
    ]
)
def test_updating(mocker, config, script_return, expected_update, n_retries):
    """Assert runner updates Cachet with expected codes"""

    try:
        completed_processes = []
        for value in script_return:
            completed_processes.append(CompletedProcessMock(value))
        mocker.patch('subprocess.run', side_effect=completed_processes)
    except TypeError:
        mocker.patch('subprocess.run', return_value=CompletedProcessMock(script_return))

    mocker.patch('cachetclient.cachet.Components.put')
    component = 99

    with pytest.raises(SystemExit):
        unit.main(script=mocker.Mock(), component_id=component, config_file=config, script_args=[],
                  retries=n_retries)

    cachetclient.cachet.Components.put.assert_called_with(
        id=component,
        status=unit.codes_mapping[expected_update])


def test_incompatible_plugin(mocker, config):
    """Assert runner fails if monitoring script is not Nagios-compatible"""

    return_code = max(c.value for c in Codes) + 1

    mock_execution = mocker.Mock()
    mock_execution.returncode = return_code

    mocker.patch('subprocess.run', return_value=mock_execution)
    mocker.patch('cachetclient.cachet.Components.put')

    common.run_and_assert(unit.main, expected_code=Codes.CRITICAL, script=mocker.Mock(),
                          component_id=99, config_file=config, script_args=[], retries=0)
    assert not cachetclient.cachet.Components.put.called


def test_unknown_no_update(mocker, config):
    """Assert Cachet is not updated if monitoring script result is UNKNOWN"""

    mock_execution = mocker.Mock()
    mock_execution.returncode = Codes.UNKNOWN.value

    mocker.patch('subprocess.run', return_value=mock_execution)
    mocker.patch('cachetclient.cachet.Components.put')

    common.run_and_assert(unit.main, expected_code=Codes.UNKNOWN, script=mocker.Mock(),
                          component_id=99, config_file=config, script_args=[], retries=0)

    assert not cachetclient.cachet.Components.put.called


def test_wait(mocker, config):
    """Assert runner waits before re-running the monitoring script"""

    mock_execution = mocker.Mock()
    mock_execution.returncode = Codes.CRITICAL.value

    mocker.patch('subprocess.run', return_value=mock_execution)
    mocker.patch('cachetclient.cachet.Components.put')
    mocker.patch('time.sleep')

    n_retries = 5
    d_interval = 10

    with pytest.raises(SystemExit):
        unit.main(script=mocker.Mock(), component_id=99, config_file=config, retries=n_retries,
                  interval=d_interval)

    expected_calls = [call(10), call(10), call(10), call(10), call(10)]

    assert time.sleep.call_args_list == expected_calls
