"""
Nagios-compatible plugin to check a resource availability over HTTP/HTTPS.
By default it is considered to be in an OK status if the HTTP status code is
200 and in a CRITICAL status otherwise, different behaviours may be specified
using optional arguments.
"""

import argparse
import logging
from urllib.parse import urlparse
import requests

from . import nagios_common as nagios

parser = argparse.ArgumentParser(
    prog='cnto-http-monitor',
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    'url',
    help='address of resource to monitor (http/https), must be '
         'properlyformatted (i.e. http://sld.tld[:port] or http://127.0.0.1'
         '[:port])'
)
parser.add_argument(
    '--timeout',
    default=30,
    type=int,
    help='maximum time (in seconds) to wait for a response, after which the'
         'resource is considered in CRITICAL status '
)
parser.add_argument(
    '--redirect-unknown',
    action='store_true',
    help='if enabled a 302 status code will result in UNKNOWN status. If'
         'disabled a 302 status code will result in CRITICAL status'
)
parser.add_argument(
    '--debug',
    action='store_true',
    default=False,
    help='display debug messages, DO NOT enable in actual Nagios use'
)


def valid_http_url(url):
    """Check if a string is a valid URL compliant to RFC2396"""

    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        return True
    return False


def main(url, timeout=30, redirect_unknown=True, debug=False):
    """Actual monitoring execution"""

    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)

    if debug:  # pragma: no cover
        logger.setLevel(logging.DEBUG)
        logger.info('debug logging enabled')

    # Check if URL is valid
    logger.debug('perform URL validation check')
    if not valid_http_url(url):
        nagios.plugin_exit(nagios.Codes.UNKNOWN, 'provided URL is not valid')

    # Send a HEAD request
    logger.debug('send HEAD request')
    try:
        response = requests.head(url, timeout=timeout)
    except requests.ConnectTimeout:
        nagios.plugin_exit(nagios.Codes.CRITICAL, 'connection timeout')
    except requests.ReadTimeout:
        nagios.plugin_exit(nagios.Codes.CRITICAL, 'no response received before'
                                                  'timeout')
    except requests.ConnectionError:
        nagios.plugin_exit(nagios.Codes.UNKNOWN, 'connection error')
    else:
        logger.debug('response received')
        if response.status_code == requests.codes.ok:
            # Response is OK
            nagios.plugin_exit(nagios.Codes.OK,
                               'status code is %d' % response.status_code)
        elif redirect_unknown and response.status_code == requests.codes.found:
            # Redirect considered as UNKNOWN
            nagios.plugin_exit(nagios.Codes.UNKNOWN,
                               'redirection with code %d' %
                               response.status_code)
        else:
            # Other code, considered not working
            nagios.plugin_exit(nagios.Codes.CRITICAL,
                               'status code is %d' % response.status_code)


def http_entry_point():  # pragma: no cover
    """Console entry point"""

    args = parser.parse_args()

    main(**args.__dict__)


if __name__ == '__main__':  # pragma: no cover
    http_entry_point()
