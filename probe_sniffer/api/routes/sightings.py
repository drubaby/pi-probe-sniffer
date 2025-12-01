from enum import Enum
from fastapi import APIRouter, Query
from probe_sniffer.api.schemas import Sighting, SightingsResponse
from probe_sniffer.storage.queries import get_sightings, get_recent_sightings


class SortOrder(str, Enum):
    """Sort order for sightings"""
    ASC = "ASC"
    DESC = "DESC"


router = APIRouter(prefix="/sightings", tags=["sightings"])


@router.get("/", response_model=SightingsResponse)
def list_sightings(
    mac: str | None = Query(None, description="Filter by device MAC address"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    order: SortOrder = Query(SortOrder.DESC, description="Sort order by timestamp")
):
    """
    List sightings with optional filtering and pagination.

    Query params:
        mac: Filter by device MAC address (optional)
        limit: Maximum results (1-1000, default 100)
        offset: Skip N results (for pagination)
        order: Sort by timestamp (ASC or DESC, default DESC)
    """
    sightings, total = get_sightings(mac=mac, limit=limit, offset=offset, order=order.value)
    return {
        "sightings": sightings,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/recent", response_model=list[Sighting])
def recent_sightings(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results")
):
    """
    Get the most recent sightings.

    Query params:
        limit: Maximum results (1-500, default 50)
    """
    return get_recent_sightings(limit=limit)
