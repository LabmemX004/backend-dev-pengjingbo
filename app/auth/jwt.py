import os, uuid, jwt
from datetime import datetime, timedelta, timezone

JWT_SECRET = os.getenv("JWT_SECRET", "dev_access")
ACCESS_TTL  = int(os.getenv("ACCESS_TTL_SECONDS", "900"))

def _now(): return datetime.now(timezone.utc)

def create_access_token(*, user_id:int, email:str, username:str, roles:list[str]) -> str:
    payload = {
        "user_id": str(user_id),
        "email": email,
        "username": username,
        "roles": roles,
        "iat": _now(),
        "exp": _now() + timedelta(seconds=ACCESS_TTL),
        "jti": str(uuid.uuid4()),
        "type": "access",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_access_token(token:str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

#/////////////////////////////////////////////////////verify access token/////////////////////////////////
    