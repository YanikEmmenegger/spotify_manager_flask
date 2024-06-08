#!/bin/bash

# Define source and destination directories
SOURCE_DIR="SpotifyViteApp/dist"
DEST_DIR="SpotifyFlaskApp/app/static"

# Copy the build files to the static directory
echo "Copying build files from $SOURCE_DIR to $DEST_DIR..."
cp -r $SOURCE_DIR/* $DEST_DIR

# Check if the copy was successful
if [ $? -eq 0 ]; then
    echo "Build files copied successfully."
else
    echo "Error copying build files." >&2
    exit 1
fi

# Start Docker containers
echo "Starting Docker containers..."
docker-compose up -d --build

# Check if Docker started successfully
if [ $? -eq 0 ]; then
    echo "Docker containers started successfully."
else
    echo "Error starting Docker containers." >&2
    exit 1
fi