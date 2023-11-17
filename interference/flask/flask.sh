#!/bin/bash
# flask settings
cd /home/jblake1/flask
export FLASK_PORT=5002
export FLASK_DEBUG=0
export FLASK_APP=/home/jblake1/flask/app.py
export PYTHONPATH=/home/jblake1/.local/lib/python3.8/site-packages
nohup flask run --host 0.0.0.0  --port $FLASK_PORT >flask.log 2>&1 &

