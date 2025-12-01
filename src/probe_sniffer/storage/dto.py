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
