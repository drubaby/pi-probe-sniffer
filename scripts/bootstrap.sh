#!/bin/bash
# Complete one-time setup of remote host

set -e

# Load config
if [ ! -f .env ]; then
    echo "Error: .env not found."
    echo ""
    echo "Run: cp .env.example .env"
    echo "Then edit .env with your remote host details and production config"
    exit 1
fi

set -a
source .env
set +a

REMOTE="${DEPLOY_USER}@${DEPLOY_HOST}"
REMOTE_PATH="${DEPLOY_PATH:-/opt/probe-sniffer}"

echo "=== Bootstrapping ${REMOTE} ==="
echo ""

# Step 1: System setup
echo "[1/5] Installing system dependencies..."
scp scripts/setup-remote.sh ${REMOTE}:/tmp/setup-remote.sh
ssh -t ${REMOTE} "sudo bash /tmp/setup-remote.sh ${DEPLOY_USER}"
ssh ${REMOTE} "rm /tmp/setup-remote.sh"

# Step 2: Sync everything (including .env this one time)
echo ""
echo "[2/5] Syncing all code and config..."
rsync -avz --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='logs/' \
    --exclude='.venv' \
    --exclude='*.egg-info' \
    ./ ${REMOTE}:${REMOTE_PATH}/

# Step 3: Set permissions
echo ""
echo "[3/5] Setting permissions..."
ssh ${REMOTE} "chmod +x ${REMOTE_PATH}/start.sh ${REMOTE_PATH}/scripts/*.sh"

# Step 4: Install Python deps
echo ""
echo "[4/5] Installing Python dependencies..."
ssh ${REMOTE} "cd ${REMOTE_PATH} && \
    (command -v uv >/dev/null || export PATH=\"\$HOME/.local/bin:/usr/local/bin:\$PATH\") && \
    uv venv && \
    uv pip install -e ."

# Step 5: Install systemd service + passwordless sudo
echo ""
echo "[5/5] Installing systemd service..."
ssh -t ${REMOTE} "sudo cp ${REMOTE_PATH}/config/systemd/probe-sniffer.service /etc/systemd/system/ && \
    sudo systemctl daemon-reload && \
    sudo systemctl enable probe-sniffer && \
    echo '${DEPLOY_USER} ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart probe-sniffer, /usr/bin/systemctl stop probe-sniffer, /usr/bin/systemctl start probe-sniffer, /usr/bin/systemctl status probe-sniffer, /usr/bin/systemctl is-active probe-sniffer, /usr/bin/journalctl' | sudo tee /etc/sudoers.d/probe-sniffer && \
    sudo chmod 0440 /etc/sudoers.d/probe-sniffer"

echo ""
echo "=== Bootstrap Complete! ==="
echo ""
echo "Now run: make deploy"
