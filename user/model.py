from typing import Optional
from pydantic import BaseModel

class CreatingOrReplacingUser(BaseModel):
    name: str
    age: int

class UpdatingUser(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None

class User(BaseModel):
    id: str
    name: str
    age: int
    created_at: str
    updated_at: str

    @classmethod
    def parse(cls, document) -> 'User':
        return User(
            id=str(document['_id']),
            name=document['name'],
            age=document['age'] if 'age' in document else 0,
            created_at=str(document['created_at']),
            updated_at=str(document['updated_at']),
        )
