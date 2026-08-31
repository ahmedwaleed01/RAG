from pydantic import BaseModel, EmailStr, Field
from bson.objectid import ObjectId
from typing import Optional

class User(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    email: EmailStr
    hashed_password: str

    class Config:
        arbitrary_types_allowed = True