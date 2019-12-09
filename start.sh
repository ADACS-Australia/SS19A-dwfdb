#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Activate the virtual environment
source ${DIR}/venv/bin/activate

# Start the python daemon using the port provided as the first argument
APP_SETTINGS="config.DevelopmentConfig" python ${DIR}/manage.py runserver -h 172.25.0.1
