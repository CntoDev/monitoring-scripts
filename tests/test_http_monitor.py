import pytest

from cnto_incident_detection import http_monitor
from cnto_incident_detection import nagios_common


def assert_nagios_exit(expected_code, exit_info, stdout):
    """Common assertions to test Nagios compatibility"""
    if not isinstance(expected_code, nagios_common.Codes):
        raise ValueError('expected_code must be an instance of cnto_incident_detection.nagios_common.Codes')

    assert exit_info == expected_code.value
    assert stdout.startswith(expected_code.name + ':')


def invalid_url(url, capfd):
    """Assert that status is UNKNOWN with wrong URL"""
    with pytest.raises(SystemExit) as exit_info:
        http_monitor.main(url)

    out, err = capfd.readouterr()
    assert_nagios_exit(nagios_common.Codes.UNKNOWN, exit_info.value.code, out)

def test_invalid_url_invalid_protocol(capfd):
    """Assert that status is UNKNOWN with wrong URL protocol"""
    url = 'htt://foo.bar'

    invalid_url(url, capfd)

def test_invalid_url_invalid_domain(capfd):
    """Assert that status is UNKNOWN with wrong URL domain"""
    url = 'http://foo'

    invalid_url(url, capfd)
