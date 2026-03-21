import json
import logging
from datetime import date
from pathlib import Path
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models.skilltap_execution_result_model import SkillTapExecutionResultModel, Contribution
from database import get_client
from service.contribution_entries_service import ContributionEntriesService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the FastAPI application."""
    # Startup context
    try:
        db = get_client()
        # Verify connection by pinging the admin database
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        # Depending on requirements, we can choose to raise or just log
    
    yield  # The app runs during this yield
    
    # Shutdown context
    try:
        db = get_client()
        db.close()
        logger.info("Successfully disconnected from MongoDB.")
    except Exception as e:
        logger.error(f"Error disconnecting from MongoDB: {e}")

app = FastAPI(
    title="SkillTap Automation API",
    description="API for accessing SkillTap execution results.",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific domains if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Set up Jinja2 Templates (Resolved dynamically for Vercel functions compatibility)
BASE_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", tags=["Dashboard"])
async def serve_dashboard(request: Request):
    """Serve the premium visual dashboard dynamically using Jinja2 Server-Side Configuration."""
    try:
        # Sort chronologically (Newest -> Oldest)
        contribution_service = ContributionEntriesService()
        contribution_data = await contribution_service.get_contribution_entries()
        sorted_data = sorted(contribution_data, key=lambda x: x["time_log_date"], reverse=True)
        
        display_entries = []
        for index, entry in enumerate(sorted_data):
            display_entries.append({
                "time_log_date": entry["time_log_date"],
                "execution_status": entry["execution_status"],
                "contributions": entry["contributions"],
                "delay": round(0.3 + (index * 0.1), 2)
            })
            
        # Calculate pythonic insights 
        total_days = len(sorted_data)
        success_days = sum(1 for d in display_entries if d["execution_status"] == "Success")
        rate = round((success_days / total_days) * 100) if total_days > 0 else 0
        
        # Calculate cumulative Top project
        project_totals = {}
        for entry in sorted_data:
            for c in entry["contributions"]:
                project_totals[c["project_name"]] = project_totals.get(c["project_name"], 0) + c["project_contribution"]
                
        top_project = "-"
        if project_totals:
            top_project = max(project_totals.items(), key=lambda x: x[1])[0]

        return templates.TemplateResponse(
            "dashboard.html", 
            {
                "request": request,
                "entries": display_entries,
                "insights": {
                    "total_days": total_days,
                    "success_rate": rate,
                    "top_project": top_project
                }
            }
        )
    except Exception as e:
        logger.error(f"Failed to render dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error loading template")

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