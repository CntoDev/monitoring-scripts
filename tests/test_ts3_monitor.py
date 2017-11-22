"""Test suite for monitoring_scripts.ts3_monitor"""

import socket
import pytest

from monitoring_scripts import ts3_monitor as unit
from monitoring_scripts.nagios_common import Codes
from . import common


# pylint: disable-msg=too-many-arguments
def run_and_assert(capfd, expected_code=Codes.OK, expected_message_part=None,
                   host='ts.some.server', port=9987, timeout=10, debug=False):
    """Provides standard arguments to be passed to test_utils.run_and_assert"""

    common.run_and_assert(unit.main, expected_code=expected_code, capfd=capfd,
                          expected_message=expected_message_part, host=host, port=port,
                          timeout=timeout, debug=debug)


def test_invalid_host(capfd, mocker):
    """Assert UNKNOWN status with invalid server hostname/address"""

    mocker.patch('socket.socket.sendto', side_effect=socket.gaierror)

    run_and_assert(capfd=capfd, expected_code=Codes.UNKNOWN)


def test_response_timeout(mocker, capfd):
    """Assert CRITICAL status if timeout is exceeded"""

    mocker.patch('socket.socket.sendto', side_effect=socket.timeout)

    run_and_assert(capfd=capfd, expected_code=Codes.CRITICAL)


@pytest.mark.parametrize(
    'response_string,expected_code,message_part',
    [
        ('invalidtsstring', Codes.CRITICAL, 'invalid'),
        (unit.VALID_CONNECTION_STRING+'something', Codes.OK, 'successful')
    ]
)
def test_with_response(capfd, mocker, response_string, expected_code,
                       message_part):
    """Assert CRITICAL status if response is invalid or OK if response is valid"""

    response = response_string.encode(unit.ENCODING_FORMAT)

    mock_socket = mocker.Mock()
    mock_socket.return_value.recv.return_value = response
    mocker.patch('socket.socket', side_effect=mock_socket)

    run_and_assert(capfd=capfd, expected_message_part=message_part,
                   expected_code=expected_code)
