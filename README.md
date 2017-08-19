[![Build Status](https://travis-ci.org/CntoDev/monitoring-scripts.svg?branch=dev)](https://travis-ci.org/CntoDev/monitoring-scripts)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/99618c1812b541af8fe600cebe4ecbef)](https://www.codacy.com/app/enricoghdn/monitoring-scripts?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CntoDev/monitoring-scripts&amp;utm_campaign=Badge_Grade)

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

 - `http-monitor`: check a resource availability over HTTP/HTTPS. By default the resource is considered to be in a `OK` status if the HTTP status code is 200 and in `CRITICAL` status otherwise, different behaviours may be specified using optional arguments.

## Planned scripts

 - `ts3-monitor`: check the status of a TeamSpeak3 server
 - `arma3-monitor`: check the status of an Arma3 server