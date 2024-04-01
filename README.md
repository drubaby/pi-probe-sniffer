# PiSniffer

Probe Request Packet Sniffer designed to run on a Raspberry Pi with a USB wireless card in monitor mode.

## Hardware

### Required
- Raspberry Pi
- USB Wireless Card capable of monitor mode
- USB Drive (to capture logs)

### Hardware setup

The wireless card will be detected and put into monitor mode by start.sh but we will want the usb drive to auto-mount on startup.
1. run `sudo blkid` to find the `PARTUUID` of the usb drive
2. add the following line to `/etc/fstab` where PARTUUID matches your device id

```bash
PARTUUID=24f4a1c2-233b-cf49-a147-137e81505db0 /media/usb ntfs defaults,auto,nofail,x-systemd,device-timeout=30, -o umask=000 0 0
```

## Installation

1. Clone repository to raspberry pi
2. Make scripts executable with `sudo chmod +x start.sh` and `sudo chmod +x setup.sh`
3. Run `sudo bash ./setup.sh` for initial setup (Do this only once! See Optional Setup for steps to do this manually)

---
### Optional Setup
Run these steps to manually set up the `setup.sh` steps
1. Install linux dependencies:

    ```bash
    sudo apt-get install -y aircrack-ng git python3-pip
    ```
2. Copy systemd service to local systemd directory, reload daemon and start service
3.
   ```bash
      #copy local service to systemd dir
      sudo cp probe-sniffer.service /etc/systemd/system/
      sudo systemctl daemon-reload
      sudo systemctl enable probe-sniffer.service
      sudo systemctl start probe-sniffer.service
    ```
---

4. Run start script
   - Run with: `sudo ./start.sh`
