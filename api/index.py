import logging
from datetime import date
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.skilltap_execution_result_model import SkillTapExecutionResultModel, Contribution

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SkillTap Automation API",
    description="API for accessing SkillTap execution results.",
    version="1.0.0"
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mock_data: List[SkillTapExecutionResultModel] = [
    SkillTapExecutionResultModel(
        time_log_date=date(2026, 3, 22),
        execution_date=date(2026, 3, 22),
        execution_status="Success",
        contributions=[
            Contribution(
                project_name="SkillTap1",
                project_contribution=10
            ),
            Contribution(
                project_name="SkillTap2",
                project_contribution=90
            ),
        ]
    )
]

@app.get("/", tags=["Root"])
async def hello_world():
    """Root endpoint to verify the API is running."""
    return {"message": "Hello from Vercel Serverless!"}

@app.get("/sync", tags=["Sync"])
async def run_sync():
    """Trigger the sync process."""
    try:
        # Placeholder for actual sync logic
        logger.info("Sync triggered successfully.")
        return {"status": "Sync triggered successfully"}
    except Exception as e:
        logger.error(f"Error during sync: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during sync")

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "OK"}

@app.get("/daily-contribution", response_model=List[SkillTapExecutionResultModel], tags=["Contributions"])
async def get_daily_contribution():
    """Retrieve daily contributions."""
    try:
        if not mock_data:
            raise HTTPException(status_code=404, detail="No contributions found")
        return mock_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch contributions: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch daily contributions")