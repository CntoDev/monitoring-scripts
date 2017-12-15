"""Test suite for check_runner"""

from unittest.mock import call

import pytest

from monitoring_scripts import check_runner as unit
from monitoring_scripts.nagios_common import Codes
from . import common


class CompletedProcessMock():  # pylint: disable=R0903
    """Mocks subprocess.CompletedProcess to test returncode"""

    def __init__(self, returncode):
        self.returncode = returncode


@pytest.fixture(scope='module')
def config(tmpdir_factory, base_url='http://some.url', api_key='namaste'):  # pylint: disable=W0621
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

    config_file = config(tmpdir_factory, base_url=base_url, api_key=api_key)

    with pytest.raises(ValueError) as excinfo:
        unit.main(script=mocker.Mock(), component_id=99, config_file=config_file)

    assert 'invalid configuration' in str(excinfo.value)


@pytest.mark.parametrize(
    'script_return,expected_update,n_retries',
    [
        (Codes.OK.value, Codes.OK, 0),
        (Codes.CRITICAL.value, Codes.CRITICAL, 0),
        ((Codes.CRITICAL.value, Codes.WARNING.value, Codes.CRITICAL.value), Codes.CRITICAL, 2),
        ((Codes.CRITICAL.value, Codes.CRITICAL.value, Codes.OK.value), Codes.OK, 2),
        ((Codes.CRITICAL.value, Codes.WARNING.value, Codes.WARNING.value), Codes.WARNING, 2),
        ((Codes.CRITICAL.value, Codes.WARNING.value, Codes.OK.value), Codes.OK, 2),
    ]
)
def test_updating(mocker, config, script_return, expected_update,  # pylint: disable=W0621
                  n_retries):
    """Assert runner updates Cachet with expected codes"""

    try:
        completed_processes = []
        for value in script_return:
            completed_processes.append(CompletedProcessMock(value))
        mocker.patch('subprocess.run', side_effect=completed_processes)
    except TypeError:
        mocker.patch('subprocess.run', return_value=CompletedProcessMock(script_return))

    cachet_update = mocker.patch('cachetclient.cachet.Components.put')
    component = 99

    with pytest.raises(SystemExit):
        unit.main(script=mocker.Mock(), component_id=component, config_file=config, script_args=[],
                  retries=n_retries)

    cachet_update.assert_called_with(id=component, status=unit.codes_mapping[expected_update])


def test_incompatible_plugin(mocker, config):  # pylint: disable=W0621
    """Assert runner fails if monitoring script is not Nagios-compatible"""

    return_code = max(c.value for c in Codes) + 1

    mock_execution = mocker.Mock()
    mock_execution.returncode = return_code

    mocker.patch('subprocess.run', return_value=mock_execution)
    cachet_update = mocker.patch('cachetclient.cachet.Components.put')

    common.run_and_assert(unit.main, expected_code=Codes.CRITICAL, script=mocker.Mock(),
                          component_id=99, config_file=config, script_args=[], retries=0)

    assert not cachet_update.called


def test_unknown_no_update(mocker, config):  # pylint: disable=W0621
    """Assert Cachet is not updated if monitoring script result is UNKNOWN"""

    mock_execution = mocker.Mock()
    mock_execution.returncode = Codes.UNKNOWN.value

    mocker.patch('subprocess.run', return_value=mock_execution)
    cachet_update = mocker.patch('cachetclient.cachet.Components.put')

    common.run_and_assert(unit.main, expected_code=Codes.UNKNOWN, script=mocker.Mock(),
                          component_id=99, config_file=config, script_args=[], retries=0)

    assert not cachet_update.called


def test_wait(mocker, config):  # pylint: disable=W0621
    """Assert runner waits before re-running the monitoring script"""

    mock_execution = mocker.Mock()
    mock_execution.returncode = Codes.CRITICAL.value

    mocker.patch('subprocess.run', return_value=mock_execution)
    mocker.patch('cachetclient.cachet.Components.put')
    time_sleep = mocker.patch('time.sleep')

    n_retries = 5
    d_interval = 10

    with pytest.raises(SystemExit):
        unit.main(script=mocker.Mock(), component_id=99, config_file=config, retries=n_retries,
                  interval=d_interval)

    expected_calls = [call(10), call(10), call(10), call(10), call(10)]

    assert time_sleep.call_args_list == expected_calls
