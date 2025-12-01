from pydantic import BaseModel
from datetime import datetime


class Device(BaseModel):
    """Complete device with all fields"""

    name: str | None = None
    mac: str
    first_seen: str
    last_seen: str
    is_trusted: bool = False

    class Config:
        from_attributes = True  # Allows conversion from sqlite3.Row


class DeviceUpdate(Device):
    """Fields that can be updated via API"""

    pass


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
