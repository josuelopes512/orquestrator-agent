"""Expert schemas for API requests and responses."""

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ExpertMatch(BaseModel):
    """Schema for a matched expert with confidence."""
    reason: str = Field(..., description="Why this expert was identified")
    confidence: Literal["high", "medium", "low"] = Field(..., description="Confidence level of the match")
    identified_at: str = Field(..., description="ISO timestamp when expert was identified")
    knowledge_summary: Optional[str] = Field(None, description="Brief summary from expert's knowledge base")
    matched_keywords: List[str] = Field(default_factory=list, description="Keywords that matched")


class ExpertTriageRequest(BaseModel):
    """Request schema for expert triage endpoint."""
    card_id: str = Field(..., alias="cardId", description="ID of the card to triage")
    title: str = Field(..., description="Card title")
    description: Optional[str] = Field(None, description="Card description")

    class Config:
        populate_by_name = True


class ExpertTriageResponse(BaseModel):
    """Response schema for expert triage endpoint."""
    success: bool = Field(..., description="Whether triage was successful")
    card_id: str = Field(..., alias="cardId", description="ID of the card")
    experts: Dict[str, ExpertMatch] = Field(default_factory=dict, description="Identified experts")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        populate_by_name = True


class ExpertSyncRequest(BaseModel):
    """Request schema for expert sync endpoint."""
    card_id: str = Field(..., alias="cardId", description="ID of the card")
    experts: Dict[str, ExpertMatch] = Field(..., description="Experts to sync")

    class Config:
        populate_by_name = True


class SyncedExpert(BaseModel):
    """Result of syncing a single expert."""
    expert_id: str = Field(..., alias="expertId")
    synced: bool = Field(..., description="Whether sync was executed")
    files_changed: List[str] = Field(default_factory=list, alias="filesChanged", description="Files that triggered sync")
    message: Optional[str] = Field(None, description="Sync result message")

    class Config:
        populate_by_name = True


class ExpertSyncResponse(BaseModel):
    """Response schema for expert sync endpoint."""
    success: bool = Field(..., description="Whether sync was successful")
    card_id: str = Field(..., alias="cardId", description="ID of the card")
    synced_experts: List[SyncedExpert] = Field(default_factory=list, alias="syncedExperts")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        populate_by_name = True


class ExpertsUpdateRequest(BaseModel):
    """Request schema for updating card experts."""
    experts: Dict[str, ExpertMatch] = Field(..., description="Experts to set on card")
