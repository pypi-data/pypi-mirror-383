"""
Type definitions for mcpadserver
"""

from typing import Optional
from pydantic import BaseModel, Field


class AdRequest(BaseModel):
    """Request model for ad requests."""

    context: str = Field(..., description="Context of the query")
    user_region: Optional[str] = Field(None, description="User region (e.g., 'US')")
    placement: str = Field("inline", description="Ad placement type")


class AdResponse(BaseModel):
    """Response model for ad responses."""

    sponsor: str = Field(..., description="Sponsor name")
    content: str = Field(..., description="Ad content text")
    link: str = Field(..., description="Tracking URL")
    impression_id: str = Field(..., description="Unique impression ID")
    placement: str = Field(..., description="Placement type")
