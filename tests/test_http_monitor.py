"""Test suite for monitoring_scripts.http_monitor"""

import pytest
import requests

from monitoring_scripts import http_monitor as unit
from monitoring_scripts.nagios_common import Codes
from . import common


# pylint: disable-msg=too-many-arguments
def run_and_assert(capfd, expected_code=Codes.OK, url='http://foo.bar',
                   timeout=30, redirect_unknown=True, debug=False):
    """Provides standard arguments to be passed to test_utils.run_and_assert"""

    common.run_and_assert(unit.main, expected_code=expected_code, capfd=capfd,
                          url=url, timeout=timeout, redirect_unknown=redirect_unknown,
                          debug=debug)


def generate_response(mocker, status_code=200):
    """Generates a fake requests.Response with the specified HTTP status code"""

    response = mocker.Mock()
    response.status_code = status_code

    return response


@pytest.mark.parametrize(
    'url',
    [
        'http:/foo.bar',
        'http://'
    ]
)
def test_invalid_url(capfd, url):
    """Assert UNKNOWN status with wrong URL"""

    run_and_assert(capfd=capfd, expected_code=Codes.UNKNOWN, url=url)


@pytest.mark.parametrize(
    'exception,expected_code',
    [
        (requests.ConnectTimeout, Codes.CRITICAL),
        (requests.ReadTimeout, Codes.CRITICAL),
        (requests.ConnectionError, Codes.UNKNOWN),
    ]
)
def test_exception(mocker, capfd, exception, expected_code):
    """Assert correct status when exception is raised"""

    mocker.patch('requests.head', side_effect=exception)

    run_and_assert(capfd=capfd, expected_code=expected_code)


@pytest.mark.parametrize(
    'status_code,kwargs',
    [
        (200, {})
    ]
)
def test_nominal(mocker, capfd, status_code, kwargs):
    """Assert OK status with successful HTTP status code"""

    mocker.patch('requests.head',
                 return_value=generate_response(mocker, status_code))

    run_and_assert(capfd=capfd, expected_code=Codes.OK, **kwargs)


@pytest.mark.parametrize(
    'status_code,kwargs',
    [
        (302, {})
    ]
)
def test_unknown(mocker, capfd, status_code, kwargs):
    """Assert UNKNOWN status with successful HTTP status code"""

    mocker.patch('requests.head',
                 return_value=generate_response(mocker, status_code))

    run_and_assert(capfd=capfd, expected_code=Codes.UNKNOWN, **kwargs)


@pytest.mark.parametrize(
    'status_code,kwargs',
    [
        (302, {'redirect_unknown': False}),
        (401, {})
    ]
)
def test_critical(mocker, capfd, status_code, kwargs):
    """Assert UNKNOWN status with successful HTTP status code"""

    mocker.patch('requests.head',
                 return_value=generate_response(mocker, status_code))

    run_and_assert(capfd=capfd, expected_code=Codes.CRITICAL, **kwargs)
