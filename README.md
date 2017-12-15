[![Build Status](https://travis-ci.org/CntoDev/monitoring-scripts.svg?branch=master)](https://travis-ci.org/CntoDev/monitoring-scripts)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d4af8ca9290d444cab0c898bab6a6e94)](https://www.codacy.com/app/CNTODev/monitoring-scripts?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CntoDev/monitoring-scripts&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/d4af8ca9290d444cab0c898bab6a6e94)](https://www.codacy.com/app/CNTODev/monitoring-scripts?utm_source=github.com&utm_medium=referral&utm_content=CntoDev/monitoring-scripts&utm_campaign=Badge_Coverage)
[![Requirements Status](https://requires.io/github/CntoDev/monitoring-scripts/requirements.svg?branch=master)](https://requires.io/github/CntoDev/monitoring-scripts/requirements/?branch=master)

# CNTO Incident Detection
This repo contains the scripts used by [Carpe Noctem Tactical Operations](http://www.carpenoctem.co) to monitor the status of its online services.

Every script is compliant to the Nagios Plugins standards in order to be attached to a Nagios based monitoring system.

## Requirements
 - Python 3.5

## Installation
It is recommended to install the package under a virtual environment (for example `virtualenv`).

Installation is possible via `pip`: clone or download the repository, open a terminal window and change location to the project main folder then run `pip install .`

## Usage
 The `cnto-check-runner` script executes a program which must abide to Nagios Plugins guidelines (see
http://nagios-plugins.org/doc/guidelines.html) and updates a single component on a configured
instance of Cachet to reflect the status detected by the script. If the status detected is `WARNING`
or `CRITICAL` the runner will execute the monitoring program again for a maximum number of times
given as argument and waiting a given amount of time between each attempt. Cachet will be updated
only if the status remains either `WARNING` or `CRITICAL` after all the retries. A final status of
`CRITICAL` will trigger a status of `Major Outage` on Cachet. A final status of `WARNING` will trigger
 a status of `Partial Outage` on Cachet. As soon as `OK` status is detected (within the maximum number
of retries) a `Operational` status is forwarded to Cachet. Having custom mappings between Nagios exit codes
and Cachet statuses will be possible in the future. If the detected status is `UNKNOWN` Cachet will not be
updated.
This script is itself compatible with Nagios Plugins standards and will return a `OK` status if
Cachet has been updated (no information on the update is provided though), a `CRITICAL` status if
the executed program returned an incompatible exit code and a `UNKNOWN` status if the service status
is uncertain.
Note: if this script is used as Nagios Plugin then the `debug` option must be disabled.

## Available monitoring scripts
The following scripts are provided to monitor CNTO's services and can be used with `cnto-check-runner`:

 - `cnto-http-monitor`: checks a resource availability over HTTP/HTTPS. By default the resource is considered to be in a `OK` status if the HTTP status code is 200 and in `CRITICAL` status otherwise, different behaviours may be specified using optional arguments.
 - `cnto-ts3-monitor`: checks a TeamSpeak 3 Server availability. If the server responds to a connection requests on the client port a `OK` status is triggered, if the response exceeds the timeout a `CRITICAL` status is triggered, if the provided hostname/address is invalid a `UNKNOWN` status is triggered.
  - `cnto-arma3-monitor`: checks an Arma3 Server availability using `A2S` server queries. If the server responds a `OK` status is triggered, if the response exceeds the timeout a `CRITICAL` status is triggered, if either one of the provided hostname/address and port is invalid a `UNKNOWN` status is triggered.
