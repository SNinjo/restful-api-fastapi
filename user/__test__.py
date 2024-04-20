import time
from typing import Awaitable, List
from bson import ObjectId
from fastapi.testclient import TestClient
from datetime import datetime, UTC
from mongodb import database
import pytest
from main import app
from user import find_existing_user
from user.model import User
client = TestClient(app)
collection = database['user']

fake_user_id = '000000000000000000000000'

@pytest.mark.asyncio
async def test_find_existing_user():
    with pytest.raises(Exception):
        await find_existing_user(fake_user_id)

@pytest.fixture
async def setup_users():
    await database.drop_collection('user')

    user_id_1 = '000000000000000000000001'
    user_id_2 = '000000000000000000000002'
    await collection.insert_one({
        '_id': ObjectId(user_id_1),
        'name': 'jo',
        'age': 20,
        'created_at': datetime.fromtimestamp(0),
        'updated_at': datetime.fromtimestamp(0),
    })
    await collection.insert_one({
        '_id': ObjectId(user_id_2),
        'name': 'alan',
        'age': 21,
        'created_at': datetime.fromtimestamp(0),
        'updated_at': datetime.fromtimestamp(0),
    })
    return await find_existing_user(user_id_1), await find_existing_user(user_id_2)

def get_timestamp(string: str) -> float:
    format = '%Y-%m-%d %H:%M:%S'
    if '+' in string:
        format = '%Y-%m-%d %H:%M:%S.%f+00:00'
    elif '.' in string:
        format = '%Y-%m-%d %H:%M:%S.%f'
    return time.mktime(datetime.strptime(string, format).timetuple())

def are_times_same(time1: str, time2: str) -> bool:
    return abs(get_timestamp(time1) - get_timestamp(time2)) <= 5

def are_users_same(user: User, data: dict) -> bool:
    return (
        data['id'] == user.id
        and data['name'] == user.name
        and are_times_same(data['created_at'], user.created_at)
        and are_times_same(data['updated_at'], user.updated_at)
    )

async def get_all_users_from_database() -> List[User]:
    length = await collection.count_documents({})
    return [User.parse(user) for user in await collection.find().to_list(length)]

async def is_all_users_in_database(users: List[User]) -> bool:
    users_in_database = await get_all_users_from_database()
    if len(users) != len(users_in_database):
        return False
    for index in range(len(users)):
        if not are_users_same(users[index], dict(users_in_database[index])):
            return False
    return True

class TestGetMethod:

    @pytest.mark.asyncio
    async def test_normal(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        response = client.get(f'/users?id={user_1.id}')
        assert response.status_code == 200
        assert are_users_same(user_1, response.json()) == True
        assert await is_all_users_in_database([user_1, user_2]) == True

    @pytest.mark.asyncio
    async def test_safe(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        client.get(f'/users?id={user_1.id}')
        assert await is_all_users_in_database([user_1, user_2]) == True
        
        client.get(f'/users?id={user_2.id}')
        assert await is_all_users_in_database([user_1, user_2]) == True
        
    @pytest.mark.asyncio
    async def test_fake_user_id(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        response = client.get(f'/users?id={fake_user_id}')
        assert response.status_code == 200
        assert response.json() == None
        assert await is_all_users_in_database([user_1, user_2]) == True

class TestPostMethod:

    @pytest.mark.asyncio
    async def test_normal(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        response = client.post('/users', json={
            'name': 'john',
            'age': 22,
        })
        assert response.status_code == 200
        data = response.json()
        user_3 = User(
            id=data['id'],
            name='john',
            age=22,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        assert are_users_same(user_3, data) == True
        assert await is_all_users_in_database([user_1, user_2, user_3]) == True

        response = client.post('/users', json={
            '_id': fake_user_id,
            'id': fake_user_id,
            'fake': 'fake',
            'created_at': 0,
            'updated_at': 0,
            'name': 'johnny',
            'age': 30,
        })
        assert response.status_code == 200
        assert data['id'] != fake_user_id
        data = response.json()
        user_4 = User(
            id=data['id'],
            name='johnny',
            age=30,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        assert are_users_same(user_4, data) == True
        assert await is_all_users_in_database([user_1, user_2, user_3, user_4]) == True
        
        response = client.post('/users', json={
            'name': 'tom',
            'age': 31,
            'fake': None,
        })
        assert response.status_code == 200
        assert data['id'] != fake_user_id
        data = response.json()
        user_5 = User(
            id=data['id'],
            name='tom',
            age=31,
            created_at=str(datetime.now(UTC)),
            updated_at=str(datetime.now(UTC)),
        )
        assert are_users_same(user_5, data) == True
        assert await is_all_users_in_database([user_1, user_2, user_3, user_4, user_5]) == True

    @pytest.mark.asyncio
    async def test_wrong_parameters(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users
        
        response = client.post('/users', json={
            'name': 'john',
            'age': 'string',
        })
        assert response.status_code == 422
        assert await is_all_users_in_database([user_1, user_2]) == True
        
        response = client.post('/users', json={
            'name': 'john',
        })
        assert response.status_code == 422
        assert await is_all_users_in_database([user_1, user_2]) == True

class TestPatchMethod:

    @pytest.mark.asyncio
    async def test_normal(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        response = client.patch(f'/users?id={user_1.id}', json={
            'name': 'john',
            'age': 22,
        })
        assert response.status_code == 200
        user_1 = User(
            id=user_1.id,
            name='john',
            age=22,
            created_at=user_1.created_at,
            updated_at=str(datetime.now(UTC)),
        )
        assert are_users_same(user_1, response.json()) == True
        assert await is_all_users_in_database([user_1, user_2]) == True
        
        response = client.patch(f'/users?id={user_1.id}', json={
            '_id': fake_user_id,
            'id': fake_user_id,
            'created_at': 0,
            'updated_at': 0,
            'fake': 'fake',
            'name': 'john',
            'age': 22,
        })
        assert response.status_code == 200
        user_1 = User(
            id=user_1.id,
            name='john',
            age=22,
            created_at=user_1.created_at,
            updated_at=str(datetime.now(UTC)),
        )
        assert are_users_same(user_1, response.json()) == True
        assert await is_all_users_in_database([user_1, user_2]) == True
        
        response = client.patch(f'/users?id={user_2.id}', json={
            'name': 'jim',
        })
        assert response.status_code == 200
        user_2 = User(
            id=user_2.id,
            name='jim',
            age=user_2.age,
            created_at=user_2.created_at,
            updated_at=str(datetime.now(UTC)),
        )
        assert are_users_same(user_2, response.json()) == True
        assert await is_all_users_in_database([user_1, user_2]) == True

        response = client.patch(f'/users?id={user_1.id}', json={
        })
        assert response.status_code == 200
        user_1 = User(
            id=user_1.id,
            name=user_1.name,
            age=user_1.age,
            created_at=user_1.created_at,
            updated_at=str(datetime.now(UTC)),
        )
        assert are_users_same(user_1, response.json()) == True
        assert await is_all_users_in_database([user_1, user_2]) == True

    @pytest.mark.asyncio
    async def test_wrong_parameters(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users
        
        response = client.patch(f'/users', json={
            'name': 'john',
            'age': 30
        })
        assert response.status_code == 422
        assert await is_all_users_in_database([user_1, user_2]) == True
        
        response = client.patch(f'/users?id={user_1.id}', json={
            'age': 'string'
        })
        assert response.status_code == 422
        assert await is_all_users_in_database([user_1, user_2]) == True

    @pytest.mark.asyncio
    async def test_fake_user_id(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users
        
        response = client.patch(f'/users?id={fake_user_id}', json={
            'name': 'jo',
            'age': 20
        })
        assert response.status_code == 200
        assert response.json() == None
        assert await is_all_users_in_database([user_1, user_2]) == True

class TestPutMethod:

    @pytest.mark.asyncio
    async def test_normal(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        response = client.put(f'/users?id={user_1.id}', json={
            'name': 'john',
            'age': 22,
        })
        assert response.status_code == 200
        user_1 = User(
            id=user_1.id,
            name='john',
            age=22,
            created_at=user_1.created_at,
            updated_at=str(datetime.now(UTC)),
        )
        assert are_users_same(user_1, response.json()) == True
        assert await is_all_users_in_database([user_1, user_2]) == True
        
        response = client.put(f'/users?id={user_2.id}', json={
            '_id': fake_user_id,
            'id': fake_user_id,
            'created_at': 0,
            'updated_at': 0,
            'fake': 'fake',
            'name': 'john',
            'age': 22,
        })
        assert response.status_code == 200
        user_2 = User(
            id=user_2.id,
            name='john',
            age=22,
            created_at=user_2.created_at,
            updated_at=str(datetime.now(UTC)),
        )
        assert are_users_same(user_2, response.json()) == True
        assert await is_all_users_in_database([user_1, user_2]) == True
        
    @pytest.mark.asyncio
    async def test_idempotent(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        client.put(f'/users?id={user_1.id}', json={
            'name': 'john',
            'age': 22,
        })
        user_1 = User(
            id=user_1.id,
            name='john',
            age=22,
            created_at=user_1.created_at,
            updated_at=str(datetime.now(UTC)),
        )
        assert await is_all_users_in_database([user_1, user_2]) == True
        
        client.put(f'/users?id={user_1.id}', json={
            'name': 'john',
            'age': 22,
        })
        assert await is_all_users_in_database([user_1, user_2]) == True

    @pytest.mark.asyncio
    async def test_wrong_parameters(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        response = client.put(f'/users', json={
            'name': 'john',
            'age': 22,
        })
        assert response.status_code == 422
        assert await is_all_users_in_database([user_1, user_2]) == True
        
        response = client.put(f'/users', json={
            'name': 'john',
            'age': 'string',
        })
        assert response.status_code == 422
        assert await is_all_users_in_database([user_1, user_2]) == True

        response = client.put(f'/users', json={
            'name': 'john',
        })
        assert response.status_code == 422
        assert await is_all_users_in_database([user_1, user_2]) == True
        
        response = client.put(f'/users', json={
        })
        assert response.status_code == 422
        assert await is_all_users_in_database([user_1, user_2]) == True

    @pytest.mark.asyncio
    async def test_fake_user_id(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        response = client.put(f'/users?id={fake_user_id}', json={
            'name': 'john',
            'age': 22,
        })
        assert response.status_code == 200
        assert response.json() == None
        assert await is_all_users_in_database([user_1, user_2]) == True

class TestDeleteMethod:

    @pytest.mark.asyncio
    async def test_normal(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        response = client.delete(f'/users?id={user_1.id}')
        assert response.status_code == 200
        assert are_users_same(user_1, response.json()) == True
        assert await is_all_users_in_database([user_2]) == True
        
    @pytest.mark.asyncio
    async def test_idempotent(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        client.delete(f'/users?id={user_1.id}')
        assert await is_all_users_in_database([user_2]) == True
        
        client.delete(f'/users?id={user_1.id}')
        assert await is_all_users_in_database([user_2]) == True
    
    @pytest.mark.asyncio
    async def test_fake_user_id(self, setup_users: Awaitable[tuple[User, User]]):
        user_1, user_2 = await setup_users

        response = client.delete(f'/users?id={fake_user_id}')
        assert response.status_code == 200
        assert response.json() == None
        assert await is_all_users_in_database([user_1, user_2]) == True
