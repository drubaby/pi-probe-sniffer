"""DTOs for storage layer."""

from dataclasses import dataclass


@dataclass
class SightingDTO:
    """
    DTO for logging probe request sightings.
    """

    mac: str
    dbm: int
    ssid: str
    oui: str
    ie_fingerprint: str | None = None  # IE hash for device fingerprinting
    ie_data: list[dict] | None = None  # Full IE structure for device_fingerprints table
