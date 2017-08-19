from enum import Enum

class Codes(Enum):
    OK = 0
    WARNING = 1
    CRITICAL = 2
    UNKNOWN = 3


def plugin_exit(code, message=None):
    if not isinstance(code, Codes):
        raise ValueError('code must be an instance of cnto_incident_detection.nagios_common.Codes')
    if message:
        print(Codes(code).name + ': ' + message)
    exit(code.value)
