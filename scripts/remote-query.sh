#!/bin/bash
# Query the remote SQLite database

set -e

# Load config
set -a
source .env
set +a

REMOTE="${DEPLOY_USER}@${DEPLOY_HOST}"
DB_PATH="${DATABASE_PATH:-/var/lib/probe-sniffer/probes.db}"

# If no query provided, start interactive session
if [ -z "$1" ]; then
    echo "Opening interactive SQLite session on ${REMOTE}..."
    echo "Database: ${DB_PATH}"
    echo ""
    ssh -t ${REMOTE} "sqlite3 ${DB_PATH}"
else
    # Run the provided query
    QUERY="$1"
    ssh ${REMOTE} "sqlite3 -header -column ${DB_PATH} \"${QUERY}\""
fi
