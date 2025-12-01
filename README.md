# PiSniffer

Always-on WiFi Probe Request Packet Sniffer designed to run on a Raspberry Pi with a USB wireless card in monitor mode.

Logs probe requests from unknown devices to a daily CSV file and publishes them to an MQTT broker for home automation integrations. My instance is configured to run with a (free) Supabase DB to store known-device MAC addresses (freeing logs from clutter) and to upload a nightly digest of probes for analysis.

Future work:
- Implementing a UI I can monitor from my phone
- Discord notifications for unknown device detection

## Hardware

### Required
- Linux host (Raspberry Pi, thin client, etc.)
- USB Wireless Card capable of monitor mode

### Hardware setup

If your host has multiple WiFi interfaces (built-in + USB), you need to identify which one to use for monitor mode. The USB WiFi interface will be configured in `.env` - see instructions in `.env.example` for how to find your interface name.

## Deployment

### Initial Setup

1. Configure `.env` locally:
   ```bash
   cp .env.example .env
   # Edit .env with your remote host details and USB WiFi interface name
   ```

2. Run bootstrap (one-time setup):
   ```bash
   make bootstrap
   ```

### Deploying Changes

After making code changes:
```bash
make deploy
```

### Service Management

```bash
make status    # Check service status
make logs      # View live logs
make restart   # Restart service
```

## Development

### Setting up local environment

This project uses [UV](https://github.com/astral-sh/uv) for fast Python package management.

1. **Install UV** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Create virtual environment and install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -e .
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

### Project Structure

```
probe_sniffer/              # Main package
├── capture/                # Packet capture & monitoring
├── models/                 # Data models (Probe, Device)
├── storage/                # Database layer
└── utils/                  # Utility functions
```
---

## Acknowledgements

This project was inspired by [this blog post](https://www.lanmaster53.com/2014/10/wifi-user-detection-system/) from Tim Tomes which I read many years ago and never stopped thinking about.
Check out the forked repo on [Ryan C Butler's GitHub](https://github.com/ryancbutler/wuds/tree/master).

I also learned a lot about WiFi probes from reading [these blog posts from Adam Robinson](https://attackingpixels.com/Tracking-Mobile-Devices-Through-802.11-Probe-Request-Frames-Part-1/) from whom I copped a lot of the core python code.

