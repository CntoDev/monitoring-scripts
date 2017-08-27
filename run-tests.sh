#!/bin/bash

pytest --cov=monitoring_scripts --cov=tests --cov-report=html --cov-report=xml tests
