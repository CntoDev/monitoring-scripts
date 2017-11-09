"""Test suite for monitoring_scripts.arma3_monitor"""
import json
import os

import pytest
import socket
import valve.source.a2s

from monitoring_scripts import arma3_monitor as unit
from monitoring_scripts.nagios_common import Codes


def run_and_assert(capfd=None, expected_code=Codes.OK,
                   expected_message_part=None,
                   host='arma.server.host',
                   port=2303, timeout=10, debug=False):
    """Run ts3_monitor.main with the specified parameters and asserts that
    its output and return code match the expected return code and Nagios
    guidelines"""

    with pytest.raises(SystemExit) as exit_info:
        unit.main(host=host, port=port, timeout=timeout, debug=debug)

    assert exit_info.value.code == expected_code.value

    if capfd:
        out = capfd.readouterr()[0]
        assert out.startswith(expected_code.name + ':')

        if expected_message_part:
            assert expected_message_part in out


def load_json_fixture(file_name):
    file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'fixtures', file_name)
    with open(file_path, 'r') as json_file:
        return json.load(json_file)


def test_invalid_host(capfd, mocker):
    """Assert UNKNOWN status with invalid hostname/address"""

    mock_querier = mocker.Mock()
    mock_querier.return_value.info.side_effect = socket.gaierror
    mocker.patch('valve.source.a2s.ServerQuerier', side_effect=mock_querier)

    run_and_assert(capfd, expected_code=Codes.UNKNOWN,
                   expected_message_part='invalid hostname')


def test_no_response(mocker, capfd):
    """Assert CRITICAL status if no response is received within the timeout"""

    mock_querier = mocker.Mock()
    mock_querier.return_value.info.side_effect = valve.source.NoResponseError
    mocker.patch('valve.source.a2s.ServerQuerier', side_effect=mock_querier)

    run_and_assert(capfd, expected_code=Codes.CRITICAL,
                   expected_message_part='no response')


@pytest.mark.parametrize(
    'response,expected_code,message_part',
    [
        (load_json_fixture('a2s_response.json'), Codes.OK, 'connection '
                                                           'successful'),
        ('', Codes.CRITICAL, 'invalid response')
    ]
)
def test_with_response(capfd, mocker, response, expected_code, message_part):
    """Assert CRITICAL status if response is invalid or OK if response is 
    valid"""

    mock_querier = mocker.Mock()
    mock_querier.return_value.info.return_value = response
    mocker.patch('valve.source.a2s.ServerQuerier', side_effect=mock_querier)

    run_and_assert(capfd, expected_code=expected_code,
                   expected_message_part=message_part)
