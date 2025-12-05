"""API routes for device fingerprint queries."""

from fastapi import APIRouter, HTTPException

from probe_sniffer.storage.database import get_cursor

router = APIRouter(prefix="/fingerprints", tags=["fingerprints"])


@router.get("/")
def list_fingerprints(limit: int = 50, offset: int = 0):
    """
    List all device fingerprints with statistics.

    Query params:
    - limit: Maximum results (default 50)
    - offset: Skip N results (default 0)
    """
    with get_cursor() as cursor:
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM device_fingerprints")
        total = cursor.fetchone()["count"]

        # Get fingerprints
        cursor.execute(
            """
            SELECT
                fingerprint_id,
                identity_id,
                first_seen,
                last_seen,
                sighting_count
            FROM device_fingerprints
            ORDER BY sighting_count DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )
        fingerprints = [dict(row) for row in cursor.fetchall()]

        return {
            "fingerprints": fingerprints,
            "total": total,
            "limit": limit,
            "offset": offset
        }


@router.get("/{fingerprint_id}")
def get_fingerprint(fingerprint_id: str):
    """Get details about a specific fingerprint including SSID signature."""
    with get_cursor() as cursor:
        # Get fingerprint record
        cursor.execute(
            "SELECT * FROM device_fingerprints WHERE fingerprint_id = ?",
            (fingerprint_id,)
        )
        fingerprint = cursor.fetchone()
        if not fingerprint:
            raise HTTPException(status_code=404, detail="Fingerprint not found")

        # Get SSID signature
        cursor.execute(
            """
            SELECT DISTINCT ssid
            FROM sightings
            WHERE ie_fingerprint = ? AND ssid != 'Undirected Probe'
            ORDER BY ssid
            """,
            (fingerprint_id,)
        )
        ssids = [row["ssid"] for row in cursor.fetchall()]

        # Get unique MAC count
        cursor.execute(
            """
            SELECT COUNT(DISTINCT mac) as unique_macs
            FROM sightings
            WHERE ie_fingerprint = ?
            """,
            (fingerprint_id,)
        )
        unique_macs = cursor.fetchone()["unique_macs"]

        result = dict(fingerprint)
        result["ssid_signature"] = ssids
        result["unique_mac_count"] = unique_macs

        return result
