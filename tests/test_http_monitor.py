import pytest
import pytest_mock
import requests

from cnto_incident_detection import http_monitor
from cnto_incident_detection.nagios_common import Codes


def assert_nagios_exit(expected_code, exit_code, stdout):
    """Common assertions to test Nagios compatibility"""
    if not isinstance(expected_code, Codes):
        raise ValueError('expected_code must be an instance of cnto_incident_detection.nagios_common.Codes')

    assert exit_code == expected_code.value
    assert stdout.startswith(expected_code.name + ':')

def run_and_assert(capfd, expected_code=Codes.OK, url='http://foo.bar', timeout=30, redirect_unknown=True, debug=False):
    """Run http_monitor.main with the specified parameters and asserts that its output and return code match the
    expected return code and the Nagios guidelines"""
    with pytest.raises(SystemExit) as exit_info:
        http_monitor.main(url, timeout, redirect_unknown, debug)

    out, err = capfd.readouterr()
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

def test_connection_timeout(mocker, capfd):
    """Assert CRITICAL status if connection times out"""
    mock_head = mocker.patch('requests.head')
    mock_head.side_effect = requests.ConnectTimeout()

    run_and_assert(capfd, expected_code=Codes.CRITICAL)

def test_response_timeout(mocker, capfd):
    """Assert CRITICAL status if response times out"""
    mock_head = mocker.patch('requests.head')
    mock_head.side_effect = requests.ReadTimeout()

    run_and_assert(capfd, expected_code=Codes.CRITICAL)

def test_200_ok(mocker, capfd):
    """Assert OK status with 200 status code"""
    mock_head = mocker.patch('requests.head', return_value=generate_response(mocker, 200))

    run_and_assert(capfd, expected_code=Codes.OK)

def test_302_redirect_unknown(mocker, capfd):
    """Assert UNKNOWN status with 302 status code and option redirect_unknown enabled"""
    mock_head = mocker.patch('requests.head', return_value=generate_response(mocker, 302))

    run_and_assert(capfd, expected_code=Codes.UNKNOWN)

def test_302_redirect_critical(mocker, capfd):
    """Assert CRITICAL status with 302 status code and option redirect_unknown disabled"""
    mock_head = mocker.patch('requests.head', return_value=generate_response(mocker, 302))

    run_and_assert(capfd, expected_code=Codes.CRITICAL, redirect_unknown=False)

def test_error(mocker, capfd):
    """Assert CRITICAL status with 4xx status code"""
    mock_head = mocker.patch('requests.head', return_value=generate_response(mocker, 401))

    run_and_assert(capfd, expected_code=Codes.CRITICAL)
