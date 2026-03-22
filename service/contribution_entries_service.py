from repository.base_repository import BaseRepository

class ContributionEntriesService:
    def __init__(self):
        self.contribution_entries_repository = BaseRepository("SkillTap-Executions", "skilltap-entries")
    
    async def get_contribution_entries(self):
        return await self.contribution_entries_repository.find({})
    
    async def get_contribution_entry(self, id: str):
        return await self.contribution_entries_repository.find_one({"_id": id})

    async def get_entry_by_date(self, date_str: str):
        return await self.contribution_entries_repository.find_one({"time_log_date": date_str})
    
    async def create_contribution_entry(self, contribution_entry: dict):
        return await self.contribution_entries_repository.insert_one(contribution_entry)
    
    async def update_contribution_entry(self, id: str, contribution_entry: dict):
        return await self.contribution_entries_repository.update_one({"_id": id}, {"$set": contribution_entry})
    
    async def delete_contribution_entry(self, id: str):
        return await self.contribution_entries_repository.delete_one({"_id": id})