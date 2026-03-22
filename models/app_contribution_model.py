from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class AppProjectContribution(BaseModel):
    """Sub-model for the external app's payload mapping structure."""
    projectId: str
    percentage: int = Field(ge=0, le=100)

class AppContributionRequest(BaseModel):
    """Strictly validates the payload sent externally to the SkillTap app."""
    userId: str
    date: str
    meetingDuration: int = Field(ge=0)
    projects: List[AppProjectContribution]
    tooMuchMeetingTime: bool
    workload: str
    
    model_config = ConfigDict(populate_by_name=True)

class AppContributionResult(BaseModel):
    """Standardized response/result object returned from the automation call."""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
