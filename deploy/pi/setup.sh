#!/bin/bash
# Raspberry Pi Setup Script for Chores App
# Run this script on your Raspberry Pi after copying the ChoresApp folder

set -e

echo "=== Chores App Setup for Raspberry Pi ==="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run this script as a regular user (not root)"
    echo "Usage: ./setup.sh"
    exit 1
fi

APP_DIR="/home/pi/ChoresApp"

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "Error: ChoresApp not found at $APP_DIR"
    echo "Please copy the ChoresApp folder to /home/pi/"
    exit 1
fi

cd "$APP_DIR"

echo "1. Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv avahi-daemon

echo ""
echo "2. Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "3. Setting up avahi (mDNS) for chores.local..."
# Set hostname to 'chores'
sudo hostnamectl set-hostname chores

# Copy avahi service file
sudo cp deploy/pi/chores.service /etc/avahi/services/chores.service
sudo systemctl restart avahi-daemon

echo ""
echo "4. Installing systemd service..."
sudo cp deploy/pi/choresapp.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable choresapp
sudo systemctl start choresapp

echo ""
echo "=== Setup Complete ==="
echo ""
echo "The Chores App is now running!"
echo ""
echo "Access from iPad: http://chores.local:8080"
echo ""
echo "Useful commands:"
echo "  Check status:  sudo systemctl status choresapp"
echo "  View logs:     sudo journalctl -u choresapp -f"
echo "  Restart:       sudo systemctl restart choresapp"
echo "  Stop:          sudo systemctl stop choresapp"
echo ""
