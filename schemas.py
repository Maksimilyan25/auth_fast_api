from typing import Optional
from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
