"""Discord webhook integration for device notifications."""

import logging
import requests
from probe_sniffer import config

logger = logging.getLogger("DISCORD")

# Reusable session for connection pooling (HTTP keep-alive)
_session = requests.Session()


def send_notification(fingerprint: dict, probe_data: dict, notification_type: str) -> bool:
    """
    Send Discord webhook notification for a device fingerprint.

    Args:
        fingerprint: Device fingerprint dict from database
        probe_data: Current probe data (mac, dbm, ssid, oui)
        notification_type: "new" or "returning"

    Returns:
        True if notification sent successfully, False otherwise
    """
    if not config.DISCORD_ENABLED:
        logger.debug("Discord notifications disabled in config")
        return False

    if config.DISCORD_DRY_RUN:
        logger.info(
            f"[DRY RUN] Would send {notification_type} notification for "
            f"{notification_type} fingerprint {fingerprint['fingerprint_id']}"
            f"{probe_data}"
        )
        return True

    if not config.DISCORD_WEBHOOK_URL or "YOUR_" in config.DISCORD_WEBHOOK_URL:
        logger.warning("Discord webhook URL not configured")
        return False

    try:
        from probe_sniffer.notifications.formatter import format_device_embed

        # Build Discord embed
        embed = format_device_embed(fingerprint, probe_data, notification_type)

        # Send webhook
        payload = {
            "embeds": [embed],
            "username": "PiSniffer",
        }

        response = _session.post(config.DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()

        logger.info(f"Discord notification sent: {notification_type} device")
        return True

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Discord notification: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending Discord notification: {e}")
        return False
