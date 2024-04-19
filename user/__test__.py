from bson import ObjectId
from httpx import Response
from fastapi.testclient import TestClient
from datetime import datetime, UTC
from mongodb import database
import pytest
from main import app
from user.model import User
client = TestClient(app)

fake_user_id = '000000000000000000000000'

@pytest.fixture
async def setup_users():
    await database.drop_collection('user')
    collection = database['user']

    users = [
        User(
            id='000000000000000000000001',
            name='jo',
            age=20,
            created_at=str(datetime.fromtimestamp(0)),
            updated_at=str(datetime.fromtimestamp(0)),
        ),
        User(
            id='000000000000000000000002',
            name='alan',
            age=21,
            created_at=str(datetime.fromtimestamp(0)),
            updated_at=str(datetime.fromtimestamp(0)),
        ),
    ]
    for user in users:
        await collection.insert_one({
            '_id': ObjectId(user.id),
            'name': user.name,
            'age': user.age,
            'created_at': datetime.strptime(user.created_at),
            'updated_at': datetime.fromtimestamp(0),
        })
    await collection.insert_one({
        '_id': ObjectId(user_id_2),
        'name': 'alan',
        'age': 21,
        'created_at': datetime.fromtimestamp(0),
        'updated_at': datetime.fromtimestamp(0),
    })
    return User(id='user_id_1')

def assert_same(response: Response, user: User) -> None:
    assert response.status_code == 200
    data = response.json()


class TestGetMethod:

    @pytest.mark.asyncio
    async def test_get_normal(self, setup_users):
        user_id_1, user_id_2 = await setup_users
        response = client.get(f'/users?id={user_id_1}')
        assert response.status_code == 200
        print(response.json())##

    # def test_get_normal(self):
    #     response = client.get(f'/users?id=000000000000000000000000')
    #     assert response.status_code == 200

# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"msg": "Hello World"}