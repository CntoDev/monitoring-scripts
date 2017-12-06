"""Provide common reference to Nagios standards to every plugin"""

from enum import Enum


class Codes(Enum):
    """Collection of plugin possible plugin_exit codes"""

    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3


def plugin_exit(code, message=None):
    """Common method to end a Nagios plugin. If no message is specified the
    service status will not be printed."""

    if not isinstance(code, Codes):
        raise ValueError('code must be an instance of'
                         'monitoring_scripts.nagios_common.Codes')
    if message:
        print(code.name + ': ' + message)
    exit(code.value)
