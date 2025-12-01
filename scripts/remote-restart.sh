#!/bin/bash
# Restart probe-sniffer service on remote host

set -e

# Load config
set -a
source .env
set +a

REMOTE="${DEPLOY_USER}@${DEPLOY_HOST}"

echo "Restarting service on ${REMOTE}..."

ssh ${REMOTE} "sudo systemctl restart probe-sniffer"

sleep 2

echo ""
echo "Service restarted. Checking status..."
ssh ${REMOTE} "sudo systemctl --no-pager status probe-sniffer" || true
