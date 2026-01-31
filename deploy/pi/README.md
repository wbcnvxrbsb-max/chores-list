# Raspberry Pi Deployment

## Prerequisites

- Raspberry Pi with Raspberry Pi OS (Lite or Desktop)
- SSH access or direct terminal access
- Internet connection for initial setup

## Quick Setup

1. **Copy the ChoresApp folder to your Pi:**

   From your Mac:
   ```bash
   scp -r ~/ChoresApp pi@raspberrypi.local:/home/pi/
   ```

2. **SSH into your Pi:**
   ```bash
   ssh pi@raspberrypi.local
   ```

3. **Run the setup script:**
   ```bash
   cd /home/pi/ChoresApp
   chmod +x deploy/pi/setup.sh
   ./deploy/pi/setup.sh
   ```

4. **Access from iPad:**
   Open Safari and go to: `http://chores.local:8080`

## What the Setup Script Does

1. Installs required packages (Python, avahi-daemon)
2. Creates Python virtual environment and installs dependencies
3. Sets the Pi's hostname to "chores" for mDNS
4. Configures avahi to advertise the service
5. Installs and starts the systemd service

## Manual Management

**Check if running:**
```bash
sudo systemctl status choresapp
```

**View logs:**
```bash
sudo journalctl -u choresapp -f
```

**Restart the app:**
```bash
sudo systemctl restart choresapp
```

**Stop the app:**
```bash
sudo systemctl stop choresapp
```

**Start on boot (enabled by default):**
```bash
sudo systemctl enable choresapp
```

## Troubleshooting

**Can't access chores.local from iPad?**
1. Make sure both devices are on the same network
2. Try rebooting the Pi: `sudo reboot`
3. Check if avahi is running: `sudo systemctl status avahi-daemon`
4. Try using the Pi's IP address instead

**Find the Pi's IP address:**
```bash
hostname -I
```

**App not starting?**
```bash
sudo journalctl -u choresapp -n 50
```

## Backup

The database is stored at `/home/pi/ChoresApp/data/chores.db`

To backup:
```bash
cp /home/pi/ChoresApp/data/chores.db ~/chores-backup-$(date +%Y%m%d).db
```

To setup automatic daily backups, add this cron job:
```bash
crontab -e
```
Add:
```
0 3 * * * cp /home/pi/ChoresApp/data/chores.db /home/pi/backups/chores-$(date +\%Y\%m\%d).db
```
