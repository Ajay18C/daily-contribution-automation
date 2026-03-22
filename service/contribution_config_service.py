from typing import List, Dict, Any
from repository.base_repository import BaseRepository
from models.app_contribution_model import AppProjectContribution

class ContributionConfigService:
    def __init__(self):
        self.config_repository = BaseRepository("SkillTap-Executions", "contribution-config")
        self.config_document_id = "global_apportionment_rule"
    
    async def get_config(self) -> List[Dict[str, Any]]:
        """
        Fetches the global project contribution configuration using strict logic.
        """
        config_doc = await self.config_repository.find_one({"id": self.config_document_id})
        
        if config_doc and "projects" in config_doc:
            return config_doc["projects"]
            
        return []
    
    async def update_config(self, projects: List[AppProjectContribution]):
        """
        Atomically replaces the global project contribution configuration.
        Uses pure Pydantic mapped models structurally mapped to DB dicts.
        """
        serialized_projects = [p.model_dump() for p in projects]
        
        result = await self.config_repository.get_collection().update_one(
            {"id": self.config_document_id},
            {"$set": {"projects": serialized_projects}},
            upsert=True
        )
        return result
