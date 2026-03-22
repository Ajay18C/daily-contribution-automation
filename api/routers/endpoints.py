from fastapi import APIRouter, Depends
from models.api_payload_model import ConfigPayload, BulkPayload

from service.contribution_config_service import ContributionConfigService
from service.entry_app_service import EntryAppService

router = APIRouter(tags=["API Endpoints"])

@router.post("/api/config-contribution")
async def save_config_contribution(payload: ConfigPayload, service: ContributionConfigService = Depends()):
    """Atomically replaces the global contribution apportionment DB configuration natively mapped."""
    await service.update_config(payload.config)
    return {"status": "success"}

@router.post("/api/fill-latest")
async def trigger_fill_latest_time(
    config_service: ContributionConfigService = Depends(),
    app_service: EntryAppService = Depends()
):
    """Triggers the automated runner specifically designed for the explicitly evaluated Last Working Day."""
    config_projects = await config_service.get_config()
    result = await app_service.fill_today_time_entries(config_projects)
    return result.model_dump()

@router.post("/api/bulk-entry")
async def trigger_bulk_entry(
    payload: BulkPayload,
    config_service: ContributionConfigService = Depends(),
    app_service: EntryAppService = Depends()
):
    """Triggers the powerful automated asyncio batch processor concurrently mapping arrays over configured Date parameters."""
    config_projects = await config_service.get_config()
    result = await app_service.fill_bulk_time_entries(config_projects, payload.start_date, payload.end_date)
    return result.model_dump()
