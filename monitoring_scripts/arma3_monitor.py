"""
Nagios-compatible plugin to check an Arma3 Server availability using A2S
server queries. If the server responds a OK status is triggered, if the
response exceeds the timeout a CRITICAL status is triggered, if either one
of the provided hostname/address and port is invalid a UNKNOWN status is
triggered.
"""

import argparse
import logging
from socket import gaierror

import valve.source.a2s

from . import nagios_common as nagios

parser = argparse.ArgumentParser(
    prog='cnto-arma3-monitor',
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    'host',
    help='Arma3 Server hostname in Internet domain notation or IPv4 address'
)
parser.add_argument(
    'port',
    type=int,
    help='port for the Steam server API service'
)
parser.add_argument(
    '--timeout',
    type=int,
    default=10,
    help='maximum time (in seconds) to wait for server response'
)
parser.add_argument(
    '--debug',
    action='store_true',
    default=False,
    help='display debug messages, DO NOT enable in actual Nagios use'
)


def main(host, port, timeout=5, debug=False):
    """Actual monitoring execution"""

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if debug:  # pragma: no cover
        logger.setLevel(logging.DEBUG)
        logger.info('debug logging enabled')

    server_addr = (host, port)
    server = valve.source.a2s.ServerQuerier(server_addr, timeout=timeout)

    try:
        logger.info('trying to query the server')
        if server.info():
            logger.info('query successful, server good')
            nagios.plugin_exit(nagios.Codes.OK, 'connection successful')
        else:
            logger.info('invalid response')
            nagios.plugin_exit(nagios.Codes.CRITICAL, 'invalid response')
    except gaierror:
        logger.info('invalid hostname or port')
        nagios.plugin_exit(nagios.Codes.UNKNOWN, 'invalid hostname/address or '
                                                 'port')
    except valve.source.NoResponseError:
        logger.info('no response received from server')
        nagios.plugin_exit(nagios.Codes.CRITICAL, 'no response received from '
                                                  'server')


def arma3_entry_point():  # pragma: no cover
    """Console entry point"""

    args = parser.parse_args()

    main(**args.__dict__)


if __name__ == '__main__':  # pragma: no cover
    arma3_entry_point()
