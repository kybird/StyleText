#!/bin/bash

# Define the container name
CONTAINER_NAME="styletext-app"

# Stop and remove the container if it already exists
echo "Stopping and removing old container: $CONTAINER_NAME"
docker stop $CONTAINER_NAME >/dev/null 2>&1
docker rm $CONTAINER_NAME >/dev/null 2>&1

# Run the new container in detached mode
echo "Running new container: $CONTAINER_NAME"
docker run -d --name $CONTAINER_NAME -p 8003:8000 styletext-server