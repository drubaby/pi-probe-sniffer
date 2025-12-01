"""Database queries"""

from datetime import datetime
from probe_sniffer.storage.database import get_cursor
from probe_sniffer.storage.dto import SightingDTO


def get_trusted_devices() -> list[str]:
    """Get list of trusted device MAC addresses."""
    with get_cursor() as cursor:
        cursor.execute("SELECT mac FROM devices WHERE is_trusted = 1")
        return [row["mac"] for row in cursor.fetchall()]


def add_device(mac: str, name: str | None = None, is_trusted: bool = False):
    """
    Add or update a device.

    Args:
        mac: Device MAC address
        name: Optional friendly name for device
        is_trusted: Whether device should be filtered from logs
    """
    now = datetime.utcnow().isoformat(sep=" ", timespec="seconds")

    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO devices (mac, name, is_trusted, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(mac) DO UPDATE SET
                name = COALESCE(?, name),
                is_trusted = ?,
                last_seen = ?
        """,
            (mac, name, int(is_trusted), now, now, name, int(is_trusted), now),
        )


def is_trusted(mac: str) -> bool:
    """
    Check if device is marked as trusted.

    Args:
        mac: Device MAC address

    Returns:
        True if device is trusted, False otherwise
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT is_trusted FROM devices WHERE mac = ?", (mac,))
        row = cursor.fetchone()
        return bool(row["is_trusted"]) if row else False


def update_last_seen(mac: str):
    """
    Update the last_seen timestamp for a device.

    Args:
        mac: Device MAC address
    """
    now = datetime.utcnow().isoformat(sep=" ", timespec="seconds")

    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO devices (mac, first_seen, last_seen, is_trusted)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(mac) DO UPDATE SET last_seen = ?
        """,
            (mac, now, now, now),
        )


def log_sighting(sighting: SightingDTO):
    """
    Log a probe request sighting to the database.

    Args:
        sighting: SightingDTO containing probe data
    """
    now = datetime.utcnow().isoformat(sep=" ", timespec="seconds")

    # Ensure device exists first (for foreign key constraint)
    update_last_seen(sighting.mac)

    # Then log the sighting
    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO sightings (timestamp, mac, rssi, dbm, ssid, oui)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                now,
                sighting.mac,
                f"{sighting.dbm} dBm",  # rssi as formatted string
                sighting.dbm,  # dbm as integer for numeric queries
                sighting.ssid,
                sighting.oui,
            ),
        )
