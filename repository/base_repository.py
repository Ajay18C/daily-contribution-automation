from typing import List, Dict, Any
from database import get_client

class BaseRepository:
    def __init__(self, database_name: str, collection_name: str):
        self.database_name = database_name
        self.collection_name = collection_name
    
    def get_collection(self):
        db_wrapper = get_client()
        return db_wrapper.client[self.database_name][self.collection_name]
    
    async def insert_one(self, document: Dict[str, Any]):
        return await self.get_collection().insert_one(document)
    
    async def insert_many(self, documents: List[Dict[str, Any]]):
        return await self.get_collection().insert_many(documents)
    
    async def find_one(self, filter_query: Dict[str, Any]):
        return await self.get_collection().find_one(filter_query)
    
    async def find(self, filter_query: Dict[str, Any], length: int = None) -> List[Dict[str, Any]]:
        cursor = self.get_collection().find(filter_query)
        return await cursor.to_list(length=length)
    
    async def update_one(self, filter_query: Dict[str, Any], update: Dict[str, Any]):
        return await self.get_collection().update_one(filter_query, update)
    
    async def update_many(self, filter_query: Dict[str, Any], update: Dict[str, Any]):
        return await self.get_collection().update_many(filter_query, update)
    
    async def delete_one(self, filter_query: Dict[str, Any]):
        return await self.get_collection().delete_one(filter_query)
    
    async def delete_many(self, filter_query: Dict[str, Any]):
        return await self.get_collection().delete_many(filter_query)