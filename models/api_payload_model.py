from typing import List
from pydantic import BaseModel
from models.app_contribution_model import AppProjectContribution

class ConfigPayload(BaseModel):
    """Payload mapping validation for global config DB replacements."""
    config: List[AppProjectContribution]

class BulkPayload(BaseModel):
    """Payload mapping validation restricting start and end bounds natively."""
    start_date: str
    end_date: str
