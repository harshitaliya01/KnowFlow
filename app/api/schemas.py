from pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    email: EmailStr
    token: str

class UserLogin(BaseModel):
    email: EmailStr
    password : str

class DocumentOut(BaseModel):
    id: int
    user_id: int
    filename: str
    filepath: str
    source: str
    created_at: str
