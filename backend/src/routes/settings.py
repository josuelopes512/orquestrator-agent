"""Settings routes for auto-cleanup configuration."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/settings", tags=["settings"])


# Esquemas Pydantic
class AutoCleanupSettings(BaseModel):
    """Auto-cleanup configuration settings."""
    enabled: bool
    cleanup_after_minutes: int  # 1-1440 minutes (1 day)


class AutoCleanupResponse(BaseModel):
    """Response for auto-cleanup settings."""
    success: bool
    settings: AutoCleanupSettings


class UpdateAutoCleanupRequest(BaseModel):
    """Request to update auto-cleanup settings."""
    enabled: Optional[bool] = None
    cleanup_after_minutes: Optional[int] = None


# Em memória por enquanto (pode ser movido para DB/config file depois)
_auto_cleanup_settings = AutoCleanupSettings(
    enabled=True,
    cleanup_after_minutes=30
)


@router.get("/auto-cleanup", response_model=AutoCleanupResponse)
async def get_auto_cleanup_settings():
    """Get current auto-cleanup settings."""
    return AutoCleanupResponse(
        success=True,
        settings=_auto_cleanup_settings
    )


@router.put("/auto-cleanup", response_model=AutoCleanupResponse)
async def update_auto_cleanup_settings(request: UpdateAutoCleanupRequest):
    """Update auto-cleanup settings."""
    global _auto_cleanup_settings

    if request.enabled is not None:
        _auto_cleanup_settings.enabled = request.enabled

    if request.cleanup_after_minutes is not None:
        if request.cleanup_after_minutes < 1 or request.cleanup_after_minutes > 1440:
            raise HTTPException(
                status_code=400,
                detail="cleanup_after_minutes must be between 1 and 1440"
            )
        _auto_cleanup_settings.cleanup_after_minutes = request.cleanup_after_minutes

    return AutoCleanupResponse(
        success=True,
        settings=_auto_cleanup_settings
    )
