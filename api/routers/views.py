from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging

from service.contribution_entries_service import ContributionEntriesService
from service.contribution_config_service import ContributionConfigService

logger = logging.getLogger(__name__)

# Set up Jinja2 Templates statically mapping visual UI renders backwards to parent template folder
BASE_DIR = Path(__file__).parent.parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(tags=["UI Views"])

@router.get("/")
async def serve_dashboard(request: Request, contribution_service: ContributionEntriesService = Depends()):
    """Serve the premium visual dashboard dynamically using Jinja2 Server-Side Configuration."""
    try:
        # Sort chronologically (Newest -> Oldest)
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

@router.get("/bulk-entry")
async def show_bulk_entry(request: Request):
    """Render the logically isolated Bulk Time Entry automation run form UI."""
    return templates.TemplateResponse("bulk_entry.html", {"request": request})

@router.get("/config-contribution")
async def show_config_contribution(request: Request, service: ContributionConfigService = Depends()):
    """Render the globally abstracted Configuration panel UI instantly pulling parameters from DB."""
    projects_config = await service.get_config()
    return templates.TemplateResponse(
        "config_contribution.html", 
        {"request": request, "projects_config": projects_config}
    )
