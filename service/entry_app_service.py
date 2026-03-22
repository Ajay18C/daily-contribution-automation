import asyncio
import aiohttp
from datetime import datetime, timedelta
from config.settings import settings
from models.app_contribution_model import AppContributionRequest, AppProjectContribution, AppContributionResult
from service.contribution_entries_service import ContributionEntriesService

def get_last_working_day() -> str:
    """Iterates backwards from yesterday to find the most recent Monday-Friday."""
    target = datetime.now() - timedelta(days=1)
    while target.weekday() > 4:  # 5=Saturday, 6=Sunday
        target -= timedelta(days=1)
    return target.strftime("%Y-%m-%d")

class EntryAppService:
    def __init__(self):
        self.base_url = settings.app_url
        self.user_id = settings.app_user_id
        # Strict Decoupling: App service only speaks to Entry Service, entirely abstracted from Raw Motor DB Repositories.
        self.entries_service = ContributionEntriesService()
    
    async def login_to_app(self) -> AppContributionResult:
        """Autheticates with the external API to retrieve a JWT Bearer token."""
        url = f"{self.base_url}/auth/login"
        payload = {
            "email": settings.app_username,
            "password": settings.app_password
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return AppContributionResult(success=True, data=data)
            except Exception as e:
                return AppContributionResult(success=False, message=f"Authentication failed: {str(e)}")

    async def fill_today_time_entries(self, config_projects: list) -> AppContributionResult:
        """Dynamically submits the configured projects to the external Application API using unified asyncio helpers."""
        
        target_date = get_last_working_day()
        
        # Authenticate sequentially first before dispatching target POST
        login_result = await self.login_to_app()
        if not login_result.success or not login_result.data or "token" not in login_result.data:
            return AppContributionResult(
                success=False, 
                message=login_result.message or "Missing authentication token in external login response."
            )
            
        headers = {"Authorization": f"Bearer {login_result.data['token']}"}
        url = f"{self.base_url}/contributions"
        mapped_projects = [AppProjectContribution(**p) for p in config_projects]
        
        # Natively reuse the exact isolated asyncio execution pipeline to actively eliminate code duplication
        async with aiohttp.ClientSession() as session:
            was_success = await self._process_single_date(
                target_date, session, url, headers, mapped_projects, config_projects
            )
            
            if was_success:
                return AppContributionResult(success=True, message=f"Time entry natively logged successfully for {target_date}.")
            else:
                return AppContributionResult(
                    success=False, 
                    message=f"Halted! Network validation failed or time entry was already previously tracked for {target_date}."
                )

    async def _log_execution_status(self, target_date: str, status: str, config_projects: list, error: str = None):
        """Standardized helper persistently saving the execution outcomes uniquely securely into local metrics."""
        document = {
            "time_log_date": target_date,
            "execution_status": status,
            "contributions": [
                {"project_name": p.get("projectId", "Unknown"), "project_contribution": p.get("percentage", 0)}
                for p in config_projects
            ]
        }
        if error:
            document["error"] = error
            
        await self.entries_service.create_contribution_entry(document)

    async def _process_single_date(self, target_date_str: str, session: aiohttp.ClientSession, url: str, headers: dict, mapped_projects: list, config_projects: list) -> bool:
        """Helper routing uniquely parsed requests processing exactly one native date dynamically context switching."""
        existing_entry = await self.entries_service.get_entry_by_date(target_date_str)
        if existing_entry and existing_entry.get("execution_status") == "Success":
            return False # Skipped natively because it natively already existed
        
        payload_obj = AppContributionRequest(
            userId=self.user_id,
            date=target_date_str,
            meetingDuration=90,
            projects=mapped_projects,
            tooMuchMeetingTime=True,
            workload="high"
        )
        
        try:
            async with session.post(url, json=payload_obj.model_dump(), headers=headers) as response:
                response.raise_for_status()
                await self._log_execution_status(target_date_str, "Success", config_projects)
                return True
        except Exception as e:
            await self._log_execution_status(target_date_str, "Failed", config_projects, str(e))
            return False

    async def fill_bulk_time_entries(self, config_projects: list, start_date: str, end_date: str) -> AppContributionResult:
        """Executes the time entry automation concurrently across a given chronological date range."""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Strict bounds chronologic validation natively rejecting present/future triggers
        today_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if start_dt >= today_dt or end_dt >= today_dt:
            return AppContributionResult(success=False, message="Execution aborted: Dates mathematically cannot be today or in the future bounds.")
        if end_dt < start_dt:
            return AppContributionResult(success=False, message="Execution aborted: End Date physically cannot be before Start Date.")
        
        # Authenticate exactly once up front
        login_result = await self.login_to_app()
        if not login_result.success or not login_result.data or "token" not in login_result.data:
            return AppContributionResult(
                success=False, 
                message=login_result.message or "Missing authentication token in external login response."
            )
        
        headers = {"Authorization": f"Bearer {login_result.data['token']}"}
        url = f"{self.base_url}/contributions"
        mapped_projects = [AppProjectContribution(**p) for p in config_projects]
        
        tasks = []
        
        async with aiohttp.ClientSession() as session:
            current_dt = start_dt
            while current_dt <= end_dt:
                # Elegantly skip weekends mathematically exactly identical to business working logic
                if current_dt.weekday() > 4:
                    current_dt += timedelta(days=1)
                    continue

                target_date_str = current_dt.strftime("%Y-%m-%d")
                
                # Append execution coroutine to our asynchronous pool 
                tasks.append(
                    self._process_single_date(
                        target_date_str, session, url, headers, mapped_projects, config_projects
                    )
                )
                
                current_dt += timedelta(days=1)
                
            # Aggressively blast all endpoints in native parallel streams
            results = await asyncio.gather(*tasks)
            success_count = sum(1 for r in results if r)

        return AppContributionResult(
            success=True,
            message=f"Parallel Bulk Automation completed. Successfully logged entries for {success_count} missing days natively."
        )