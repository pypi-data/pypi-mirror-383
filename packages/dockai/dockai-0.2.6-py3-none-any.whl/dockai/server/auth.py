import jwt, os
from fastapi import HTTPException, Header

SECRET = os.getenv("JWT_SECRET", "dockai_secret")

def get_current_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Auth header missing")
    try:
        token = authorization.split(" ")[1]
        user = jwt.decode(token, SECRET, algorithms=["HS256"])
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
