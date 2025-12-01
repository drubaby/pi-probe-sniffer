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

# Step 5: Setup database directory with correct permissions
echo ""
echo "[5/7] Setting up database directory..."
ssh ${REMOTE} "sudo mkdir -p ${DATABASE_PATH%/*} && \
    sudo chown -R ${DEPLOY_USER}:${DEPLOY_USER} ${DATABASE_PATH%/*} && \
    sudo chmod 775 ${DATABASE_PATH%/*}"

# Step 6: Install systemd services
echo ""
echo "[6/7] Installing systemd services..."
# Generate API service file with correct user
mkdir -p /tmp/probe-sniffer-bootstrap
sed "s/{{DEPLOY_USER}}/${DEPLOY_USER}/g" \
    config/systemd/probe-sniffer-api.service > /tmp/probe-sniffer-bootstrap/probe-sniffer-api.service
scp /tmp/probe-sniffer-bootstrap/probe-sniffer-api.service ${REMOTE}:/tmp/
rm -rf /tmp/probe-sniffer-bootstrap

ssh -t ${REMOTE} "sudo cp ${REMOTE_PATH}/config/systemd/probe-sniffer.service /etc/systemd/system/ && \
    sudo mv /tmp/probe-sniffer-api.service /etc/systemd/system/ && \
    sudo systemctl daemon-reload && \
    sudo systemctl enable probe-sniffer probe-sniffer-api"

# Step 7: Configure passwordless sudo (simpler pattern)
echo ""
echo "[7/7] Configuring passwordless sudo..."
ssh -t ${REMOTE} "echo '${DEPLOY_USER} ALL=(ALL) NOPASSWD: /bin/systemctl, /bin/journalctl, /bin/chown, /bin/chmod, /bin/mkdir' | sudo tee /etc/sudoers.d/probe-sniffer && \
    sudo chmod 0440 /etc/sudoers.d/probe-sniffer"

echo ""
echo "=== Bootstrap Complete! ==="
echo ""
echo "Now run: make deploy"
