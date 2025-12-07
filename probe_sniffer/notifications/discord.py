"""Discord notification integration."""

import logging
import requests

logger = logging.getLogger("DISCORD")


def post_discord_notification(fingerprint: dict, probe_data: dict, notification_type: str) -> bool:
    """
    Post a notification to the Discord bot via the local API.

    Args:
        fingerprint: Device fingerprint dict from database
        probe_data: Current probe data (mac, dbm, ssid, oui)
        notification_type: "new" or "returning"

    Returns:
        True if notification posted successfully, False otherwise
    """
    try:
        response = requests.post(
            "http://localhost:8000/internal/notify",
            json={
                "fingerprint": fingerprint,
                "probe_data": probe_data,
                "notification_type": notification_type,
            },
            timeout=5,
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to post Discord notification: {e}")
        return False
