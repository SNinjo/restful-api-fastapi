from pydantic import BaseModel

class UserAttribute(BaseModel):
    name: str
    age: int

class User(UserAttribute):
    _id: str
    name: str
    age: int
    created_at: str
    updated_at: str
