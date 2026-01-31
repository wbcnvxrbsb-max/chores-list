# Mac Deployment

## Quick Start (Manual)

Run the start script to launch the app:

```bash
cd ~/ChoresApp
./deploy/mac/start.sh
```

Access from iPad: `http://chores.local:8080`

## Auto-Start on Login (LaunchAgent)

To have the app start automatically when you log in:

1. Copy the plist file:
```bash
cp ~/ChoresApp/deploy/mac/com.choresapp.plist ~/Library/LaunchAgents/
```

2. Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.choresapp.plist
```

3. The app will now start automatically on login.

To stop:
```bash
launchctl unload ~/Library/LaunchAgents/com.choresapp.plist
```

To check status:
```bash
launchctl list | grep choresapp
```

## Accessing from iPad

1. Make sure iPad is on the same WiFi network as your Mac
2. Open Safari on iPad
3. Go to: `http://chores.local:8080`

Note: The `.local` domain uses Bonjour/mDNS, which is built into macOS and iOS.

## Troubleshooting

**Can't access from iPad?**
- Ensure both devices are on the same WiFi network
- Try the IP address instead: `http://<mac-ip>:8080`
- Check if the server is running: `curl http://localhost:8080`

**View logs:**
```bash
tail -f /tmp/choresapp.log
tail -f /tmp/choresapp.error.log
```
