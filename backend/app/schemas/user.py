from pydantic import BaseModel, EmailStr


class UserCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
