#!/bin/bash
# Get the directory of the script to robustly find the project root
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Building Docker image from context: $DIR/.."
docker build -t styletext-server -f "$DIR/Dockerfile" "$DIR/.."