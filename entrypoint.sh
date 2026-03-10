#!/bin/bash

CONFIG_FILE=$1

if [ -z "$CONFIG_FILE" ]; then
    echo "Usage: docker run solar-panel-sim <scenario.json>"
    exit 1
fi

CONFIG_PATH="/app/config/$CONFIG_FILE"

python /app/src/main.py "$CONFIG_PATH"