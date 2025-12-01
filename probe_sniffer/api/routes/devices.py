from fastapi import APIRouter, HTTPException
from probe_sniffer.api.schemas import Device, DeviceUpdate, DeviceWithStats
from probe_sniffer.storage.queries import (
    get_device,
    get_all_devices,
    update_device,
)
from probe_sniffer.storage.database import get_cursor

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/", response_model=list[Device])
def list_devices(is_trusted: bool | None = None):
    """
    List all devices, optionally filtered by trusted status.

    Query params:
        is_trusted: Filter by trusted status (true/false/null for all)
    """
    devices = get_all_devices(is_trusted=is_trusted)

    # Enrich devices with OUI and SSIDs from sightings
    with get_cursor() as cursor:
        for device in devices:
            # Get most recent OUI for this device
            cursor.execute(
                "SELECT oui FROM sightings WHERE mac = ? AND oui IS NOT NULL ORDER BY timestamp DESC LIMIT 1",
                (device["mac"],)
            )
            oui_row = cursor.fetchone()
            device["oui"] = oui_row["oui"] if oui_row else None

            # Get unique SSIDs this device has probed for
            cursor.execute(
                "SELECT DISTINCT ssid FROM sightings WHERE mac = ? AND ssid IS NOT NULL AND ssid != '' ORDER BY ssid",
                (device["mac"],)
            )
            ssid_rows = cursor.fetchall()
            device["ssids"] = [row["ssid"] for row in ssid_rows]

    return devices


@router.get("/{mac}", response_model=DeviceWithStats)
def get_device_details(mac: str):
    """
    Get device details with statistics.

    Path params:
        mac: Device MAC address (e.g., aa:bb:cc:dd:ee:ff)
    """
    device = get_device(mac)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # Get statistics and enrich with OUI/SSIDs
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) as count, AVG(dbm) as avg_dbm FROM sightings WHERE mac = ?",
            (mac,)
        )
        stats = cursor.fetchone()

        # Get most recent OUI
        cursor.execute(
            "SELECT oui FROM sightings WHERE mac = ? AND oui IS NOT NULL ORDER BY timestamp DESC LIMIT 1",
            (mac,)
        )
        oui_row = cursor.fetchone()

        # Get unique SSIDs
        cursor.execute(
            "SELECT DISTINCT ssid FROM sightings WHERE mac = ? AND ssid IS NOT NULL AND ssid != '' ORDER BY ssid",
            (mac,)
        )
        ssid_rows = cursor.fetchall()

    return {
        **device,
        "total_sightings": stats["count"],
        "avg_signal_dbm": stats["avg_dbm"],
        "oui": oui_row["oui"] if oui_row else None,
        "ssids": [row["ssid"] for row in ssid_rows],
    }


@router.put("/{mac}", response_model=Device)
def update_device_info(mac: str, device_update: DeviceUpdate):
    """
    Update device name and/or trusted status.

    Path params:
        mac: Device MAC address

    Body:
        name: Friendly name for device
        is_trusted: Whether to filter this device from logs
    """
    # Check device exists
    existing = get_device(mac)
    if not existing:
        raise HTTPException(status_code=404, detail="Device not found")

    # Update device
    update_device(
        mac=mac,
        name=device_update.name,
        is_trusted=device_update.is_trusted,
    )

    # Return updated device with OUI and SSIDs
    updated = get_device(mac)

    with get_cursor() as cursor:
        # Get most recent OUI
        cursor.execute(
            "SELECT oui FROM sightings WHERE mac = ? AND oui IS NOT NULL ORDER BY timestamp DESC LIMIT 1",
            (mac,)
        )
        oui_row = cursor.fetchone()

        # Get unique SSIDs
        cursor.execute(
            "SELECT DISTINCT ssid FROM sightings WHERE mac = ? AND ssid IS NOT NULL AND ssid != '' ORDER BY ssid",
            (mac,)
        )
        ssid_rows = cursor.fetchall()

    return {
        **updated,
        "oui": oui_row["oui"] if oui_row else None,
        "ssids": [row["ssid"] for row in ssid_rows],
    }
