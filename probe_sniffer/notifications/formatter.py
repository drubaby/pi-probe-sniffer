"""Discord message formatting utilities."""

from datetime import datetime


def format_device_embed(fingerprint: dict, probe_data: dict, notification_type: str) -> dict:
    """
    Format a Discord embed for a device notification.

    Args:
        fingerprint: Device fingerprint dict from database
        probe_data: Current probe data (mac, dbm, ssid, oui)
        notification_type: "new" or "returning"

    Returns:
        Discord embed dict
    """
    # Determine color based on notification type
    # Blurple for new devices, green for returning devices
    color = 0x5865F2 if notification_type == "new" else 0x57F287

    # Build title
    if notification_type == "new":
        title = "🆕 New Device Detected"
    else:
        title = "🔄 Device Returned"

    # Build fields
    fields = [
        {"name": "Manufacturer", "value": probe_data.get("oui", "Unknown"), "inline": True},
        {"name": "Signal", "value": f"{probe_data.get('dbm', 'N/A')} dBm", "inline": True},
        {
            "name": "Sighting Count",
            "value": str(fingerprint.get("sighting_count", 0)),
            "inline": True,
        },
        {
            "name": "First Seen",
            "value": datetime.utcnow(fingerprint.get("first_seen")),
            "inline": True,
        },
    ]

    # Add last_seen for returning devices
    if notification_type == "returning":
        fields.append(
            {"name": "Last Seen", "value": fingerprint.get("last_seen", "Unknown"), "inline": True}
        )

    # Add current SSID if available
    ssid = probe_data.get("ssid", "Undirect Probe")
    fields.append({"name": "Currently Probing", "value": ssid, "inline": False})

    # Build embed
    fingerprint_id = fingerprint.get("fingerprint_id", "Unknown")
    embed = {
        "title": title,
        "color": color,
        "fields": fields,
        "footer": {"text": f"Fingerprint: {fingerprint_id[:16]}..."},
        "timestamp": datetime.utcnow().isoformat(),
    }

    return embed
