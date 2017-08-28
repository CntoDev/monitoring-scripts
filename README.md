[![Build Status](https://travis-ci.org/CntoDev/monitoring-scripts.svg?branch=master)](https://travis-ci.org/CntoDev/monitoring-scripts)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d4af8ca9290d444cab0c898bab6a6e94)](https://www.codacy.com/app/CNTODev/monitoring-scripts?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CntoDev/monitoring-scripts&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/d4af8ca9290d444cab0c898bab6a6e94)](https://www.codacy.com/app/CNTODev/monitoring-scripts?utm_source=github.com&utm_medium=referral&utm_content=CntoDev/monitoring-scripts&utm_campaign=Badge_Coverage)

# CNTO Incident Detection
This repo contains the scripts used by [Carpe Noctem Tactical Operations](http://www.carpenoctem.co) to monitor the status of its online services.

Every script is compliant to the Nagios standards in order to be attached to a Nagios based monitoring system.

## Requirements
 - Python 3.5

## Installation
It is recommended to install the package under a virtual environment (for example `virtualenv`).

Installation is possible via `pip`: clone or download the repository, open a terminal window and change location to the project main folder then run
`pip install .`

## Available scripts

 - `cnto-http-monitor`: check a resource availability over HTTP/HTTPS. By default the resource is considered to be in a `OK` status if the HTTP status code is 200 and in `CRITICAL` status otherwise, different behaviours may be specified using optional arguments.

## Planned scripts

 - `ts3-monitor`: check the status of a TeamSpeak3 server
 - `arma3-monitor`: check the status of an Arma3 server