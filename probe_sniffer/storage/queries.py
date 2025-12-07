"""Database queries"""

import json
from datetime import datetime
from probe_sniffer.storage.database import get_cursor
from probe_sniffer.storage.dto import SightingDTO
from probe_sniffer.utils.time_utils import UTC, utc_now, utc_now_iso


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
    now = utc_now_iso()

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
    now = utc_now_iso()

    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO devices (mac, first_seen, last_seen, is_trusted)
            VALUES (?, ?, ?, 0)
            ON CONFLICT(mac) DO UPDATE SET last_seen = ?
        """,
            (mac, now, now, now),
        )


def upsert_device_fingerprint(fingerprint_id: str, ie_data: list[dict] | None):
    """
    Create or update a device fingerprint record.

    Args:
        fingerprint_id: The IE fingerprint hash
        ie_data: Full IE structure as list of dicts
    """
    if not fingerprint_id or fingerprint_id == "no_stable_ies":
        return  # Skip invalid fingerprints

    now = utc_now_iso()
    ie_data_json = json.dumps(ie_data) if ie_data else None

    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO device_fingerprints (fingerprint_id, ie_data, first_seen, last_seen, sighting_count)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(fingerprint_id) DO UPDATE SET
                last_seen = ?,
                sighting_count = sighting_count + 1
        """,
            (fingerprint_id, ie_data_json, now, now, now),
        )


def get_device_fingerprint(fingerprint_id: str) -> dict | None:
    """
    Get a device fingerprint record by ID.

    Args:
        fingerprint_id: The IE fingerprint hash

    Returns:
        Fingerprint dict or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM device_fingerprints WHERE fingerprint_id = ?", (fingerprint_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def should_notify_fingerprint(fingerprint: dict) -> tuple[bool, str]:
    """
    Checks fingerprint table for "notification_enabled" to determine if a Discord notification should be sent
    As a safeguard, does not send notifications for devices seen 100+ times to avoid spamming myself

    Args:
        fingerprint: Device fingerprint dict from database

    Returns:
        Tuple of (should_notify: bool, notification_type: "new"|"returning"|"")
    """
    if not fingerprint:
        return (False, "")

    # Check if notifications are enabled for this fingerprint
    if not fingerprint.get("notification_enabled", 1):
        return (False, "")

    sighting_count = fingerprint.get("sighting_count", 0)

    # Spam filter: don't notify for neighbor IoT devices (>100 sightings)
    if sighting_count > 100:
        print(f"[Discord] Not pushing notification for {fingerprint} seen {sighting_count} times.")
        return (False, "")

    # New device: first time seeing this fingerprint
    if sighting_count == 1:
        return (True, "new")

    # Returning device: detect arrival by gap in last_seen
    last_seen = fingerprint.get("last_seen")
    if last_seen:
        try:
            # Parse as UTC (database stores UTC timestamps)
            last_seen_dt = datetime.fromisoformat(last_seen).replace(tzinfo=UTC)
            now = utc_now()
            minutes_since = (now - last_seen_dt).total_seconds() / 60

            # If device was away for 10+ minutes, it's a new arrival
            if minutes_since >= 10:
                return (True, "returning")
        except (ValueError, TypeError):
            pass

    return (False, "")


def log_sighting(sighting: SightingDTO) -> dict | None:
    """
    Log a probe request sighting to the database.

    Args:
        sighting: SightingDTO containing probe data

    Returns:
        OLD fingerprint dict (before update) for notification logic, or None
    """
    now = utc_now_iso()

    # Ensure device exists first (for foreign key constraint)
    update_last_seen(sighting.mac)

    # Fetch OLD fingerprint BEFORE updating (for arrival detection)
    old_fingerprint = None
    if sighting.ie_fingerprint and sighting.ie_data:
        old_fingerprint = get_device_fingerprint(sighting.ie_fingerprint)

        # Now update the fingerprint (updates last_seen to now)
        upsert_device_fingerprint(sighting.ie_fingerprint, sighting.ie_data)

    # Then log the sighting
    with get_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO sightings (timestamp, mac, rssi, dbm, ssid, oui, ie_fingerprint)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                now,
                sighting.mac,
                f"{sighting.dbm} dBm",  # rssi as formatted string
                sighting.dbm,  # dbm as integer for numeric queries
                sighting.ssid,
                sighting.oui,
                sighting.ie_fingerprint,
            ),
        )

    return old_fingerprint


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
    mac: str | None = None, limit: int = 100, offset: int = 0, order: str = "DESC"
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
        cursor.execute("SELECT * FROM sightings ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]


def create_device_identity(
    identity_id: str, alias: str | None = None, fingerprint_ids: list[str] | None = None
) -> dict:
    """
    Create a new device identity.

    Args:
        identity_id: Unique identifier for the device identity
        alias: User-friendly name for the device
        fingerprint_ids: List of fingerprint IDs to link to this identity

    Returns:
        The created device identity dict
    """
    now = utc_now_iso()

    with get_cursor() as cursor:
        # Create the identity
        cursor.execute(
            """
            INSERT INTO device_identities (identity_id, alias, alias_set_at, first_seen, last_seen, total_sightings)
            VALUES (?, ?, ?, ?, ?, 0)
        """,
            (identity_id, alias, now if alias else None, now, now),
        )

        # Link fingerprints to this identity if provided
        if fingerprint_ids:
            for fingerprint_id in fingerprint_ids:
                cursor.execute(
                    """
                    UPDATE device_fingerprints
                    SET identity_id = ?
                    WHERE fingerprint_id = ?
                """,
                    (identity_id, fingerprint_id),
                )

        # Get and return the created identity
        cursor.execute("SELECT * FROM device_identities WHERE identity_id = ?", (identity_id,))
        return dict(cursor.fetchone())


def update_device_identity_alias(identity_id: str, alias: str) -> dict | None:
    """
    Update the alias for a device identity.

    Args:
        identity_id: The device identity ID
        alias: New alias

    Returns:
        Updated device identity dict or None if not found
    """
    now = utc_now_iso()

    with get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE device_identities
            SET alias = ?, alias_set_at = ?
            WHERE identity_id = ?
        """,
            (alias, now, identity_id),
        )

        if cursor.rowcount == 0:
            return None

        cursor.execute("SELECT * FROM device_identities WHERE identity_id = ?", (identity_id,))
        return dict(cursor.fetchone())


def get_device_identity(identity_id: str) -> dict | None:
    """
    Get a device identity by ID.

    Args:
        identity_id: The device identity ID

    Returns:
        Device identity dict or None if not found
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM device_identities WHERE identity_id = ?", (identity_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_device_identities() -> list[dict]:
    """
    Get all device identities.

    Returns:
        List of device identity dicts
    """
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM device_identities ORDER BY last_seen DESC")
        return [dict(row) for row in cursor.fetchall()]


def link_fingerprint_to_identity(fingerprint_id: str, identity_id: str):
    """
    Link a fingerprint to a device identity.

    Args:
        fingerprint_id: The fingerprint hash
        identity_id: The device identity ID
    """
    with get_cursor() as cursor:
        cursor.execute(
            """
            UPDATE device_fingerprints
            SET identity_id = ?
            WHERE fingerprint_id = ?
        """,
            (identity_id, fingerprint_id),
        )


def disable_fingerprint_notifications(fingerprint_id: str):
    """Disable notifications for a fingerprint (called from bot button)."""
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE device_fingerprints SET notification_enabled = 0 WHERE fingerprint_id = ?",
            (fingerprint_id,),
        )


def set_fingerprint_alias(fingerprint_id: str, alias: str) -> str:
    """
    Set an alias for a fingerprint by creating or updating its identity.

    Args:
        fingerprint_id: The fingerprint hash
        alias: User-friendly name for the device

    Returns:
        The identity_id (same as fingerprint_id for simplicity)
    """
    now = utc_now_iso()

    with get_cursor() as cursor:
        # Check if fingerprint already has an identity
        cursor.execute(
            "SELECT identity_id FROM device_fingerprints WHERE fingerprint_id = ?",
            (fingerprint_id,),
        )
        row = cursor.fetchone()
        existing_identity_id = row["identity_id"] if row else None

        if existing_identity_id:
            # Update existing identity alias
            cursor.execute(
                "UPDATE device_identities SET alias = ?, alias_set_at = ? WHERE identity_id = ?",
                (alias, now, existing_identity_id),
            )
            return existing_identity_id
        else:
            # Create new identity using fingerprint_id as identity_id
            cursor.execute(
                """
                INSERT INTO device_identities (identity_id, alias, alias_set_at, first_seen, last_seen, total_sightings)
                VALUES (?, ?, ?, ?, ?, 0)
                """,
                (fingerprint_id, alias, now, now, now),
            )
            # Link fingerprint to this identity
            cursor.execute(
                "UPDATE device_fingerprints SET identity_id = ? WHERE fingerprint_id = ?",
                (fingerprint_id, fingerprint_id),
            )
            return fingerprint_id
