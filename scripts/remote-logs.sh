#!/bin/bash
# Tail logs from remote probe-sniffer service

set -e

# Load config
set -a
source .env
set +a

REMOTE="${DEPLOY_USER}@${DEPLOY_HOST}"

echo "Tailing logs from ${REMOTE}..."
echo "Press Ctrl+C to exit"
echo ""

ssh ${REMOTE} "sudo journalctl -u probe-sniffer -f"
