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


def get_device(mac: str) -> dict | None:
    """
    Get a single device by MAC address.

    Returns:
        Device dict or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM devices WHERE mac = ?", (mac,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_devices(is_trusted: bool | None = None) -> list[dict]:
    """
    Get all devices, optionally filtered by trusted status.

    Args:
        is_trusted: Filter by trusted status (None = all devices)

    Returns:
        List of device dicts
    """
    with get_cursor() as cursor:
        if is_trusted is None:
            cursor.execute("SELECT * FROM devices ORDER BY last_seen DESC")
        else:
            cursor.execute(
                "SELECT * FROM devices WHERE is_trusted = ? ORDER BY last_seen DESC",
                (int(is_trusted),),
            )
        return [dict(row) for row in cursor.fetchall()]


def update_device(mac: str, name: str | None = None, is_trusted: bool | None = None):
    """
    Update device name and/or trusted status.

    Args:
        mac: Device MAC address
        name: New name (None to skip update)
        is_trusted: New trusted status (None to skip update)
    """
    with get_cursor() as cursor:
        # Build dynamic update query
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)

        if is_trusted is not None:
            updates.append("is_trusted = ?")
            params.append(int(is_trusted))

        if updates:
            query = f"UPDATE devices SET {', '.join(updates)} WHERE mac = ?"
            params.append(mac)
            cursor.execute(query, params)


def get_sightings(
    mac: str | None = None,
    limit: int = 100,
    offset: int = 0,
    order: str = "DESC"
) -> tuple[list[dict], int]:
    """
    Get sightings with optional filtering and pagination.

    Args:
        mac: Filter by device MAC address
        limit: Maximum number of results
        offset: Number of results to skip
        order: Sort order ("ASC" or "DESC")

    Returns:
        Tuple of (sightings list, total count)
    """
    with get_cursor() as cursor:
        # Build query
        where_clause = "WHERE mac = ?" if mac else ""
        params = [mac] if mac else []

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM sightings {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()["count"]

        # Get sightings
        query = f"""
            SELECT * FROM sightings
            {where_clause}
            ORDER BY timestamp {order}
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        sightings = [dict(row) for row in cursor.fetchall()]

        return sightings, total


def get_recent_sightings(limit: int = 50) -> list[dict]:
    """
    Get the most recent sightings.

    Args:
        limit: Maximum number of results

    Returns:
        List of recent sightings
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM sightings ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]
