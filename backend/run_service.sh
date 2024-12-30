#!/bin/bash

SERVICE_NAME=$1
PORT=$2

if [ -z "$SERVICE_NAME" ] || [ -z "$PORT" ]; then
    echo "Usage: ./run_service.sh <service-name> <port>"
    echo "Example: ./run_service.sh prediction-service 8001"
    exit 1
fi

# Set the Python path to include the backend directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the service
python -m ${SERVICE_NAME}.app.main
