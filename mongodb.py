from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = 'mongodb://root:pass@localhost:27017'
client = AsyncIOMotorClient(MONGO_URL)
database = client['test']

import asyncio
async def test():
    collection = database['user']
    data = await collection.find_one({'_id': '66210b8204b9ae6ef45add16'})
    print(data)
asyncio.run(test())
