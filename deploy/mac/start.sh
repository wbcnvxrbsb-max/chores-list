#!/bin/bash
# Start Chores App on Mac with mDNS registration
# This script starts the Flask server and registers it as chores.local

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$APP_DIR"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the Flask server
echo "Starting Chores App..."
echo "Access locally at: http://localhost:8080"
echo "Access from iPad at: http://chores.local:8080"
echo ""
echo "Press Ctrl+C to stop"

# Register the service with Bonjour (runs in background)
# The service will be advertised as _http._tcp with name "Chores"
dns-sd -R "Chores" _http._tcp local 8080 &
DNS_SD_PID=$!

# Trap to clean up dns-sd on exit
cleanup() {
    echo ""
    echo "Stopping Chores App..."
    kill $DNS_SD_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Run the server
python server/app.py
