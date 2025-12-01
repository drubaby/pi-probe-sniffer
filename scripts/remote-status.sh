#!/bin/bash
# Check probe-sniffer service status on remote host

set -e

# Load config
set -a
source .env
set +a

REMOTE="${DEPLOY_USER}@${DEPLOY_HOST}"

echo "Checking service status on ${REMOTE}..."
echo ""

ssh ${REMOTE} "sudo systemctl --no-pager status probe-sniffer"
