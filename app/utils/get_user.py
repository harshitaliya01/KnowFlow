from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException, Depends
from app.core.security import decode_access_token

auth_schema = HTTPBearer()


def get_current_user(cred: HTTPAuthorizationCredentials = Depends(auth_schema)):
    token = cred.credentials
    try:
        payload = decode_access_token(token)
        email = payload["sub"]
        if not email:
            raise HTTPException(status_code=401, detail="Invalid Or Expired Token1")
        
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid Or Expired Token2")

    return {"email": email}