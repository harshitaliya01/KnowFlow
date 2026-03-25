from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.utils.limit import limiter
from app.db.session import get_db
from app.db.models import User
from app.api.schemas import UserOut, UserCreate, UserLogin
from app.core.security import create_access_token,hash_paasword, verify_password

router = APIRouter()

@router.get("/health1")
@limiter.limit("5/minute")
async def health1(request:Request):
    return {"health":"Done"}

@router.post("/auth/signup", response_model=UserOut)
async def signup(user: UserCreate, db: AsyncSession= Depends(get_db)):
    try:
        result = await db.execute(select(User).where(User.email == user.email))

    except Exception as e:
        raise HTTPException(status_code=500,detail="Internal Server Error")
    
    if result.scalar():
        raise HTTPException(status_code=400,detail="Email Alreday Exist")
    new_user = User(
        email = user.email,
        password = hash_paasword(user.password)
    )
    db.add(new_user)
    await db.commit()
    token = create_access_token({"sub" : new_user.email})
    return{
        "email": new_user.email,
        "token": token
    }

@router.post("/auth/login", response_model=UserOut)
async def login(user: UserLogin, db:AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user.email))
    db_user = result.scalar()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid Email Or Password")
    
    token = create_access_token({"sub":db_user.email})
    return{
        "email":db_user.email,
        "token":token
    }
