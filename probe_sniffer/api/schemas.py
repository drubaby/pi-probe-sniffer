from pydantic import BaseModel


class Device(BaseModel):
    """Complete device with all fields"""

    name: str | None = None
    mac: str
    first_seen: str
    last_seen: str
    is_trusted: bool = False
    oui: str | None = None  # Manufacturer from OUI lookup
    ssids: list[str] = []  # Unique SSIDs probed
    total_sightings: int = 0  # Total number of probe requests seen

    class Config:
        from_attributes = True  # Allows conversion from sqlite3.Row


class DeviceUpdate(BaseModel):
    """Fields that can be updated via API - all optional"""

    name: str | None = None
    is_trusted: bool | None = None
    mac: str | None = None
    first_seen: str | None = None
    last_seen: str | None = None


class DeviceWithStats(Device):
    """Device with additional statistics"""

    total_sightings: int
    avg_signal_dbm: float | None = None


class Sighting(BaseModel):
    """Individual probe request sighting"""

    id: int
    timestamp: str
    mac: str
    rssi: str
    dbm: int
    ssid: str | None = None
    oui: str | None = None

    class Config:
        from_attributes = True


class SightingsResponse(BaseModel):
    """Paginated sightings response"""

    sightings: list[Sighting]
    total: int
    limit: int
    offset: int


class NotifyRequest(BaseModel):
    """Request payload for /internal/notify endpoint."""

    fingerprint: dict
    probe_data: dict
    notification_type: str
