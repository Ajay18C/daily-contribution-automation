from datetime import date
from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field, model_validator

class ExecutionStatus(str, Enum):
    """Possible statuses for automation execution."""
    SUCCESS = "Success"
    FAILED = "Failed"
    PENDING = "Pending"

class Contribution(BaseModel):
    """Represents a contribution made to a specific project."""
    
    # Prod-grade model configuration: strict parsing, disallow extra fields
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    project_name: str = Field(
        ...,
        min_length=1, 
        max_length=255, 
        description="The name of the project contributed to."
    )
    project_contribution: int = Field(
        ..., 
        gt=0, 
        le=100,
        description="The numeric value or percentage of the contribution."
    )

class SkillTapExecutionResultModel(BaseModel):
    """Represents the execution result of the SkillTap automation process."""
    
    # Prod-grade model configuration
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, frozen=True)

    time_log_date: date = Field(..., description="The date the time was logged.")
    execution_date: date = Field(..., description="The date the automation was executed.")
    execution_status: ExecutionStatus = Field(
        ..., 
        description="The status of the execution, e.g., 'Success'."
    )
    contributions: List[Contribution] = Field(
        default_factory=list, 
        description="List of contributions recorded."
    )

    @model_validator(mode="after")
    def validate_contributions(self):
        total = sum(c.project_contribution for c in self.contributions)

        if total != 100 and self.execution_status == ExecutionStatus.SUCCESS:
            raise ValueError(f"Total contribution must be 100, got {total}")

        names = [c.project_name for c in self.contributions]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate project names are not allowed")

        return self
