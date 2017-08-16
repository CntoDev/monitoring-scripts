import pytest

from cnto_incident_detection import http_monitor
from cnto_incident_detection import nagios_common

def test_invalid_url_invalid_protocol(capfd):
    """Assert that status is UNKNOWN with wrong URL protocol"""
    url = 'htt://foo.bar'

    with pytest.raises(SystemExit) as exit_info:
        http_monitor.main(url)

    assert exit_info.value.code == nagios_common.Codes.UNKNOWN.value

    out, err = capfd.readouterr()

    assert out.startswith('UNKNOWN:')
