#!/bin/bash

# Activate the virtual environment
python3 -m venv venv
source venv/bin/activate

export PYTHONPATH=$(pwd):$PYTHONPATH

python3 -m pip install -r trx/gunicorn/requirements.txt

python3 cli.py

# Deactivate the virtual environment
deactivate