"""Provide common reference to Nagios standards to every plugin"""

from enum import Enum


class Codes(Enum):
    """Collection of plugin possible exit codes"""

    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3


def plugin_exit(code, message=None):
    """Common method to end a Nagios plugin. If no message is specified the service status will
    not be printed."""

    if not isinstance(code, Codes):
        raise ValueError('code must be an instance of cnto_incident_detection.nagios_common.Codes')
    if message:
        print(Codes(code).name + ': ' + message)
    exit(code.value)
