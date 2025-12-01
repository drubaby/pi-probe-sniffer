#!/bin/bash
# One-time setup script for remote host
# Usage: setup-remote.sh [deploy_user]

set -e

if [ "$(id -u)" != "0" ]; then
   echo "Error: This script must be run as root (use sudo)"
   exit 1
fi

# Get deploy user from argument or SUDO_USER
DEPLOY_USER="${1:-$SUDO_USER}"

if [ -z "$DEPLOY_USER" ]; then
   echo "Error: Could not determine deploy user"
   exit 1
fi

echo "Setting up remote host for probe-sniffer..."

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y \
    aircrack-ng \
    wireless-tools \
    iw \
    python3 \
    python3-pip \
    python3-venv \
    rsync \
    curl \
    sqlite3

# Configure NetworkManager to ignore USB WiFi interfaces (for monitor mode)
echo "Configuring NetworkManager to ignore USB WiFi interfaces..."
mkdir -p /etc/NetworkManager/conf.d
cat > /etc/NetworkManager/conf.d/unmanaged-monitor-interface.conf << 'EOF'
# Ignore USB WiFi interfaces (wlx*) used for monitor mode
# This allows airmon-ng to configure them without interference
[keyfile]
unmanaged-devices=interface-name:wlx*
EOF
systemctl restart NetworkManager

# Install UV for fast Python package management
echo "Installing UV..."
curl -LsSf https://astral.sh/uv/install.sh | sh
# Copy UV to system-wide location (not symlink, to avoid permission issues)
cp /root/.local/bin/uv /usr/local/bin/uv
chmod +x /usr/local/bin/uv

# Create directories
echo "Creating directories..."
mkdir -p /opt/probe-sniffer
mkdir -p /var/lib/probe-sniffer
mkdir -p /var/log/probe-sniffer

# Configure passwordless sudo for deployment operations
echo "Configuring passwordless sudo for ${DEPLOY_USER}..."
cat > /etc/sudoers.d/probe-sniffer << EOF
# Probe Sniffer deployment permissions
${DEPLOY_USER} ALL=(ALL) NOPASSWD: /bin/mv /tmp/probe-sniffer.service /tmp/probe-sniffer-api.service /etc/systemd/system/
${DEPLOY_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl daemon-reload
${DEPLOY_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart probe-sniffer
${DEPLOY_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart probe-sniffer-api
${DEPLOY_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart probe-sniffer probe-sniffer-api
${DEPLOY_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl status probe-sniffer*
${DEPLOY_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl is-active probe-sniffer*
${DEPLOY_USER} ALL=(ALL) NOPASSWD: /usr/bin/journalctl*
EOF
chmod 0440 /etc/sudoers.d/probe-sniffer

# Set ownership so deploy user can write
echo "Setting ownership to ${DEPLOY_USER}..."
chown -R ${DEPLOY_USER}:${DEPLOY_USER} /opt/probe-sniffer
chown -R root:root /var/lib/probe-sniffer
chown -R root:root /var/log/probe-sniffer

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. On your development machine, configure .env with this host's details"
echo "2. On your development machine, run: make deploy"
