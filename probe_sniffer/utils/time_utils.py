"""Timestamp utilities for consistent time handling across the app."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Standard timezones
UTC = timezone.utc
EASTERN = ZoneInfo("America/New_York")


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime.

    Use this instead of deprecated datetime.utcnow().
    """
    return datetime.now(UTC)


def utc_now_iso() -> str:
    """Return current UTC time as ISO string for database storage.

    Format: 'YYYY-MM-DD HH:MM:SS' (matches existing DB format)
    """
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


def format_eastern(utc_timestamp: str | datetime | None) -> str:
    """Convert UTC timestamp to Eastern time for display.

    Args:
        utc_timestamp: ISO string from DB or datetime object

    Returns:
        Formatted string like 'Dec 07, 06:34:00 AM' or 'Unknown'
    """
    if not utc_timestamp:
        return "Unknown"

    try:
        if isinstance(utc_timestamp, str):
            dt = datetime.fromisoformat(utc_timestamp).replace(tzinfo=UTC)
        else:
            dt = utc_timestamp if utc_timestamp.tzinfo else utc_timestamp.replace(tzinfo=UTC)

        eastern_dt = dt.astimezone(EASTERN)
        return eastern_dt.strftime("%b %d, %I:%M:%S %p")
    except (ValueError, TypeError):
        return str(utc_timestamp) if utc_timestamp else "Unknown"


def get_log_time() -> str:
    """Return current Eastern time for logging.

    Format: 'YYYY-MM-DD HH:MM:SS'
    """
    return datetime.now(EASTERN).strftime("%Y-%m-%d %H:%M:%S")
