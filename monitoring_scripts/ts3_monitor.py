"""
Nagios-compatible plugin to check a TeamSpeak 3 Server availability. If the
server responds to a connection requests on the client port a OK status is
triggered, if the response exceeds the timeout a CRITICAL status is
triggered, if the provided hostname/address is invalid a UNKNOWN status is
triggered.
"""

import argparse
import logging
import socket

from . import nagios_common as nagios

parser = argparse.ArgumentParser(
    prog='cnto-ts3-monitor',
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    'host',
    help='TeamSpeak3 Server hostname in Internet domain notation or IPv4 '
         'address'
)
parser.add_argument(
    '--port',
    type=int,
    default=9987,
    help='server UDP port for connection'
)
parser.add_argument(
    '--timeout',
    type=int,
    default=10,
    help='maximum time to wait for server response'
)
parser.add_argument(
    '--debug',
    action='store_true',
    default=False,
    help='display debug messages, DO NOT enable in actual Nagios use'
)

CONNECTION_DGRAM = '545333494e495431006500008808b1e27f0059d686723b2afa6a' \
                   '0000000000000000'
VALID_CONNECTION_STRING = 'TS3'
ENCODING_FORMAT = 'cp1252'


def main(host, port=9987, timeout=10, debug=False):
    """Actual monitoring execution"""

    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)

    if debug:  # pragma: no cover
        logger.setLevel(logging.DEBUG)
        logger.info('debug logging enabled')

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)

    ts3_server = (host, port)
    message = bytes.fromhex(CONNECTION_DGRAM)

    try:
        s.sendto(message, ts3_server)
        response_bytes = s.recv(1024)

        response_string = response_bytes.decode(ENCODING_FORMAT,
                                                errors='ignore')
        if VALID_CONNECTION_STRING in response_string:
            nagios.plugin_exit(nagios.Codes.OK, 'connection successful')
        else:
            nagios.plugin_exit(nagios.Codes.CRITICAL, 'invalid server response')
    except socket.gaierror:
        nagios.plugin_exit(nagios.Codes.UNKNOWN, 'invalid host or address')
    except socket.timeout:
        nagios.plugin_exit(nagios.Codes.CRITICAL, 'response timed out')


def ts3_entry_point():  # pragma: no cover
    """Console entry point"""

    args = parser.parse_args()

    main(**args.__dict__)


if __name__ == '__main__':  # pragma: no cover
    ts3_entry_point()
