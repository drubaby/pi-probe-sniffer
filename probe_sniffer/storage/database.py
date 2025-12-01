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


def init_database():
    """Initialize db schema if it doesn't exist."""
    from probe_sniffer.storage.schema import SCHEMA

    with get_cursor() as cursor:
        cursor.executescript(SCHEMA)
