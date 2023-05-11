#!/bin/bash

# create virtual environment , activate , install dependencies
echo "Initializing virtual environment"
if [ -d ".env" ]; then
    echo "Activating virtual environment"
    . .env/bin/activate
else
    python3 -m venv .env
    . .env/bin/activate
    pip install -r requirements.txt
fi

# start flask server
echo "Starting flask server"
python main.py