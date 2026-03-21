from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

client = None

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.database_url)

    def close(self):
        self.client.close()

def get_client():
    global client
    if not client:
        client = Database()
    return client