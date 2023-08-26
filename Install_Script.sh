#!/bin/bash

# Install dependencies
echo "Installing required packages..."
sudo apt-get update
sudo apt-get install python3-pip libportaudio2 -y

# Install Python packages
echo "Installing Python packages..."
pip3 install pyaudio pushover

# Run the song detection script
echo "Running the song detection script..."
python3 song_detection.py

echo "Setup and script execution complete."
