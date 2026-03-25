from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

pwd_context = CryptContext(schemes=["argon2"],deprecated="auto")

SECRET_KEY = "123"
ALGORITHM = "HS256"

def hash_paasword(pwd: str) -> str:
    return pwd_context.hash(pwd)

def verify_password(pwd:str, hash: str) -> bool:
    return pwd_context.verify(pwd,hash)

def create_access_token(data:dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token:str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    
    except JWTError:
        return None