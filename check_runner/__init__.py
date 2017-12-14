"""
Forwards the status of a service detected by a Nagios-compatible script to a Cachet instance.
TODO: improve runner description including soft failure to hard failure details and arguments
implications
"""
import argparse
import logging
import subprocess

import time
import cachetclient.cachet as cachet

from . import settings
from monitoring_scripts import nagios_common

parser = argparse.ArgumentParser(
    prog='cnto-check-runner',
    description=__doc__,
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
    'script',
    help='path to executable script which monitors a service and returns its status with a '
         'Nagios-compatible standard'
)
parser.add_argument(
    'component_id',
    help='numerical id of Cachet\'s component',
    type=int
)
parser.add_argument(
    'config_file',
    help='path to configuration file, see config.ini.dist file for example'
)
parser.add_argument(
    '--retries',
    help='number of times to run the script before a hard failure is actually filed to Cachet',
    type=int,
    default=5
)
parser.add_argument(
    '--interval',
    help='time (in seconds) between each attempt',
    type=float,
    default=0.5
)
parser.add_argument(
    '--script-args',
    help='arguments passed to the monitoring script',
    nargs=argparse.REMAINDER,
    default=[]
)
parser.add_argument(
    '--debug',
    help='display debug messages',
    default=False,
    action='store_true'
)

codes_mapping = {
    nagios_common.Codes.OK: 1,
    nagios_common.Codes.WARNING: 4,
    nagios_common.Codes.CRITICAL: 4,
    nagios_common.Codes.UNKNOWN: None
}


def main(script, component_id, config_file, script_args=None, retries=5, interval=0.5, debug=False):
    """Script execution"""

    if script_args is None:
        script_args = []

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    if debug: # pragma: no cover
        logger.setLevel(logging.DEBUG)
        logger.info('debug logging enabled')

    # Read Cachet API parameters from config file
    config_parser = settings.RunnerConfigParser()
    config_parser.read(config_file)
    base_url = config_parser.get('Cachet', 'base-url', fallback=None)
    api_key = config_parser.get('Cachet', 'api-key', fallback=None)
    logger.info('Config params: base-url = %s, api-key = %s', base_url, api_key)
    if not api_key or not base_url:
        logger.critical('one or both mandatory config parameters are missing')
        raise ValueError('Invalid config file, use config.ini.dist file as reference')

    # Run monitoring script
    script_args.insert(0, script)
    logger.debug('invocation arguments %s', script_args)
    script_return_code = None
    remaining_attempts = retries
    while script_return_code != nagios_common.Codes.OK and remaining_attempts >= 0:
        if remaining_attempts < retries:
            # Not first run, script is in soft failure status, wait before retrying
            time.sleep(interval)
        logger.info('attempt n. %d', retries - remaining_attempts + 1)

        completed_execution = subprocess.run(script_args)
        logger.debug('execution completed, plugin exit code is %d', completed_execution.returncode)
        logger.debug('type of plugin exit code is %s', completed_execution.returncode)
        try:
            script_return_code = nagios_common.Codes(completed_execution.returncode)
        except ValueError:
            logger.critical('script plugin exit code is not compatible with Nagios standards, '
                            'return code is %d', completed_execution.returncode)
            nagios_common.plugin_exit(code=nagios_common.Codes.CRITICAL)

        logger.info('script return code is: %s, %d', script_return_code.name,
                    script_return_code.value)
        remaining_attempts -= 1

    # Update Cachet
    cachet_status_code = codes_mapping[script_return_code]
    if cachet_status_code:
        components = cachet.Components(endpoint=base_url, api_token=api_key)
        components.put(id=component_id, status=cachet_status_code)

        logger.info('updated component %d with status %d', component_id, cachet_status_code)
        nagios_common.plugin_exit(code=nagios_common.Codes.OK)
    else:
        logger.warning('no updates were sent to Cachet')
        nagios_common.plugin_exit(code=nagios_common.Codes.UNKNOWN)


def console_entry_point(): # pragma: no cover
    """Console entry point"""

    args = parser.parse_args()

    main(**args.__dict__)


if __name__ == '__main__': # pragma: no cover
    console_entry_point()
