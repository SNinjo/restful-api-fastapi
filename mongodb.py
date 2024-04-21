import os
import sys
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
load_dotenv()

client = AsyncIOMotorClient(os.environ.get('MONGO_URI'))
client.get_io_loop = asyncio.get_running_loop
database = client['restful-api'] if 'pytest' not in sys.modules else client['test']
