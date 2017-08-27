"""Test suite for monitoring_scripts.http_monitor"""

import pytest
import requests

from monitoring_scripts import http_monitor as unit
from monitoring_scripts.nagios_common import Codes


def assert_nagios_exit(expected_code, exit_code, stdout):
    """Common assertions to test Nagios compatibility"""

    assert exit_code == expected_code.value
    assert stdout.startswith(expected_code.name + ':')


def run_and_assert(capfd, expected_code=Codes.OK, url='http://foo.bar', timeout=30,
                   redirect_unknown=True, debug=False):
    """Run http_monitor.main with the specified parameters and asserts that its output and return
    code match the expected return code and the Nagios guidelines """

    with pytest.raises(SystemExit) as exit_info:
        unit.main(url, timeout, redirect_unknown, debug)

    out = capfd.readouterr()[0]
    assert_nagios_exit(expected_code, exit_info.value.code, out)


def generate_response(mocker, status_code=200):
    """Generates a fake requests.Response with the specified HTTP status code"""

    response = mocker.Mock()
    response.status_code = status_code

    return response


def invalid_url(url, capfd):
    """Assert UNKNOWN status with wrong URL"""

    run_and_assert(capfd, expected_code=Codes.UNKNOWN, url=url)


def test_invalid_url_invalid_protocol(capfd):
    """Assert UNKNOWN status with wrong URL protocol"""

    url = 'htt://foo.bar'

    invalid_url(url, capfd)


def test_invalid_url_invalid_domain(capfd):
    """Assert UNKNOWN status with wrong URL domain"""

    url = 'http://foo'

    invalid_url(url, capfd)


@pytest.mark.parametrize(
    'exception,expected_code',
    [
        (requests.ConnectTimeout, Codes.CRITICAL),
        (requests.ReadTimeout, Codes.CRITICAL),
    ]
)
def test_timeout(mocker, capfd, exception, expected_code):
    """Assert the script exits with the correct code when the requests library generates an
    exception"""

    mocker.patch('requests.head', side_effect=exception)

    run_and_assert(capfd, expected_code=expected_code)


@pytest.mark.parametrize(
    'status_code,kwargs',
    [
        (200, {})
    ]
)
def test_nominal(mocker, capfd, status_code, kwargs):
    """Assert OK status with successful HTTP status code"""

    mocker.patch('requests.head', return_value=generate_response(mocker, status_code))

    run_and_assert(capfd, expected_code=Codes.OK, **kwargs)


@pytest.mark.parametrize(
    'status_code,kwargs',
    [
        (302, {})
    ]
)
def test_unknown(mocker, capfd, status_code, kwargs):
    """Assert UNKNOWN status with successful HTTP status code"""

    mocker.patch('requests.head', return_value=generate_response(mocker, status_code))

    run_and_assert(capfd, expected_code=Codes.UNKNOWN, **kwargs)


@pytest.mark.parametrize(
    'status_code,kwargs',
    [
        (302, {'redirect_unknown': False}),
        (401, {})
    ]
)
def test_critical(mocker, capfd, status_code, kwargs):
    """Assert UNKNOWN status with successful HTTP status code"""

    mocker.patch('requests.head', return_value=generate_response(mocker, status_code))

    run_and_assert(capfd, expected_code=Codes.CRITICAL, **kwargs)
