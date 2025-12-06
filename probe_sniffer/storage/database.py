"""Database connection and initialization for SQLite."""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager

# Get database path from environment or use default
DB_PATH = Path(os.getenv("DATABASE_PATH", "/var/lib/probe-sniffer/probes.db"))


def get_connection() -> sqlite3.Connection:
    """
    Get database connection

    Returns:
        sqlite3.Connection with foreign keys enabled and row factory set
    """
    # Create parent directory if it doesn't exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # Row lets us access columns by name instead of tuple indices
    return conn


@contextmanager
def get_cursor():
    """
    Context manager for database operations with automatic commit/rollback.

    Usage:
        with get_cursor() as cursor:
            cursor.execute("INSERT INTO devices VALUES (?, ?)", (mac, name))

    Yields:
        sqlite3.Cursor
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def migrate_to_fingerprinting():
    """
    Add fingerprinting columns to existing sightings table.
    Safe to run multiple times (idempotent).
    """
    with get_cursor() as cursor:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(sightings)")
        columns = {row[1] for row in cursor.fetchall()}

        # Add ie_fingerprint column if missing
        if 'ie_fingerprint' not in columns:
            cursor.execute("ALTER TABLE sightings ADD COLUMN ie_fingerprint TEXT")
            print("✓ Added ie_fingerprint column to sightings table")

        # Add identity_id column if missing
        if 'identity_id' not in columns:
            cursor.execute(
                "ALTER TABLE sightings ADD COLUMN identity_id TEXT "
                "REFERENCES device_identities(identity_id)"
            )
            print("✓ Added identity_id column to sightings table")

        # Create indexes for new columns
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sightings_identity "
            "ON sightings(identity_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_sightings_fingerprint "
            "ON sightings(ie_fingerprint)"
        )


def migrate_to_discord_notifications():
    """
    Add Discord notification column to device_fingerprints table.
    Safe to run multiple times (idempotent).
    """
    with get_cursor() as cursor:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(device_fingerprints)")
        columns = {row[1] for row in cursor.fetchall()}

        # Add notification_enabled column if missing
        if 'notification_enabled' not in columns:
            cursor.execute(
                "ALTER TABLE device_fingerprints ADD COLUMN notification_enabled INTEGER DEFAULT 1"
            )
            print("✓ Added notification_enabled column to device_fingerprints table")


def init_database():
    """Initialize db schema if it doesn't exist."""
    from probe_sniffer.storage.schema import SCHEMA

    with get_cursor() as cursor:
        cursor.executescript(SCHEMA)

    # Run migrations
    migrate_to_fingerprinting()
    migrate_to_discord_notifications()
