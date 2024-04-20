from bson import ObjectId
from typing import Optional
from mongodb import database
from pydantic import BaseModel
from datetime import datetime, UTC
from user.model import User, CreatingOrReplacingUser, UpdatingUser
from fastapi import APIRouter
router = APIRouter(prefix='/users')
collection = database['user']

def to_dict(model: BaseModel, is_new: bool = False, is_none_filtered: bool = True) -> dict:
    data = dict(model)
    data['updated_at'] = datetime.now(UTC)
    if is_new:
        data['created_at'] = datetime.now(UTC)
    if is_none_filtered:
        data = {key: value for key, value in data.items() if data[key]}
    return data

async def find_user(id: str) -> Optional[User]:
    document = await collection.find_one({'_id': ObjectId(id)})
    return User.parse(document) if document else None
async def find_existing_user(id: str) -> User:
    user = await find_user(id)
    if user is None:
        raise Exception(f'existing user not found | id: {id}')
    return user

@router.get('')
async def get_user(id: str) -> Optional[User]:
    return await find_user(id)

@router.post('')
async def create_user(user: CreatingOrReplacingUser) -> User:
    result = await collection.insert_one(to_dict(user, is_new=True))
    return await find_existing_user(result.inserted_id)

@router.patch('')
async def update_user(id: str, user: UpdatingUser) -> Optional[User]:
    if await find_user(id):
        await collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": to_dict(user, is_none_filtered=True)}
        )
        return await find_existing_user(id)
    
@router.put('')
async def replace_user(id: str, user: CreatingOrReplacingUser) -> Optional[User]:
    if await find_user(id):
        await collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": to_dict(user)}
        )
        return await find_existing_user(id)

@router.delete('')
async def delete_user(id: str) -> Optional[User]:
    user = await find_user(id)
    if user:
        await collection.delete_one({"_id": ObjectId(id)})
        return user
