#!/bin/bash
# Deploy code changes to remote host

set -e

# Load config
set -a
source .env
set +a

REMOTE="${DEPLOY_USER}@${DEPLOY_HOST}"
REMOTE_PATH="${DEPLOY_PATH:-/opt/probe-sniffer}"

echo "Deploying to ${REMOTE}..."

# Sync code (exclude .env to protect production config)
echo "Syncing code..."
rsync -avz --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='logs/' \
    --exclude='.venv' \
    --exclude='*.egg-info' \
    ./ ${REMOTE}:${REMOTE_PATH}/

# Update Python dependencies (only if pyproject.toml changed)
echo "Checking dependencies..."
ssh ${REMOTE} "cd ${REMOTE_PATH} && \
    if [ ! -f .deps-installed ] || [ pyproject.toml -nt .deps-installed ]; then \
        echo 'Updating dependencies...' && \
        (command -v uv >/dev/null || export PATH=\"\$HOME/.local/bin:/usr/local/bin:\$PATH\") && \
        uv pip install -e . && \
        touch .deps-installed; \
    else \
        echo 'Dependencies up to date'; \
    fi"

# Restart service
echo "Restarting service..."
ssh ${REMOTE} "sudo systemctl restart probe-sniffer"

sleep 2

# Show status
echo ""
ssh ${REMOTE} "sudo systemctl --no-pager status probe-sniffer" || true

echo ""
echo "Deployment complete."
echo "Monitor logs: make logs"
