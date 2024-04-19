import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = 'mongodb://root:pass@localhost:27017'
client = AsyncIOMotorClient(MONGO_URL)
client.get_io_loop = asyncio.get_running_loop
database = client['restful-api'] if 'pytest' not in sys.modules else client['test']
