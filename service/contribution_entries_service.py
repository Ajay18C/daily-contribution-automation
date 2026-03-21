from repository.base_repository import BaseRepository

class ContributionEntriesService:
    def __init__(self):
        self.contribution_entries_repository = BaseRepository("SkillTap-Executions", "skilltap-entries")
    
    async def get_contribution_entries(self):
        return await self.contribution_entries_repository.find({})
    
    async def get_contribution_entry(self, id: str):
        return await self.contribution_entries_repository.find_one({"_id": id})
    
    # async def create_contribution_entry(self, contribution_entry: ContributionEntry):
    #     return await self.contribution_entries_repository.insert_one(contribution_entry)
    
    # async def update_contribution_entry(self, id: str, contribution_entry: ContributionEntry):
    #     return await self.contribution_entries_repository.update_one({"_id": id}, contribution_entry)
    
    async def delete_contribution_entry(self, id: str):
        return await self.contribution_entries_repository.delete_one({"_id": id})