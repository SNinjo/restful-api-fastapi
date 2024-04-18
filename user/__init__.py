from typing import List
from mongodb import database
from user.model import User
from fastapi import APIRouter
router = APIRouter(prefix='/users')
collection = database['user']

@router.get('')
async def get_users():
    cursor = await collection.find_one({'_id': '66210b8204b9ae6ef45add16'})
    print(cursor)
    return cursor

# @router.post('')
# def create_user(user: User) -> User:
#     return User(name='123', age=12)
