"""API routes for device identity management."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from probe_sniffer.storage.queries import (
    create_device_identity,
    update_device_identity_alias,
    get_device_identity,
    get_all_device_identities,
    link_fingerprint_to_identity,
)

router = APIRouter(prefix="/identities", tags=["identities"])


class CreateIdentityRequest(BaseModel):
    """Request to create a device identity."""

    identity_id: str
    alias: str | None = None
    fingerprint_ids: list[str] | None = None


class UpdateAliasRequest(BaseModel):
    """Request to update an identity alias."""

    alias: str


class LinkFingerprintRequest(BaseModel):
    """Request to link a fingerprint to an identity."""

    fingerprint_id: str


@router.get("/")
def list_identities():
    """List all device identities."""
    return get_all_device_identities()


@router.get("/{identity_id}")
def get_identity(identity_id: str):
    """Get a specific device identity."""
    identity = get_device_identity(identity_id)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    return identity


@router.post("/")
def create_identity(request: CreateIdentityRequest):
    """Create a new device identity."""
    try:
        return create_device_identity(
            identity_id=request.identity_id,
            alias=request.alias,
            fingerprint_ids=request.fingerprint_ids,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{identity_id}/alias")
def update_alias(identity_id: str, request: UpdateAliasRequest):
    """Update the alias for a device identity."""
    identity = update_device_identity_alias(identity_id, request.alias)
    if not identity:
        raise HTTPException(status_code=404, detail="Identity not found")
    return identity


@router.post("/{identity_id}/fingerprints")
def link_fingerprint(identity_id: str, request: LinkFingerprintRequest):
    """Link a fingerprint to a device identity."""
    try:
        link_fingerprint_to_identity(request.fingerprint_id, identity_id)
        return {"message": "Fingerprint linked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
