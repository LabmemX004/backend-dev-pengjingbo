import os, uuid, jwt
from datetime import datetime, timedelta, timezone

JWT_SECRET = os.getenv("JWT_SECRET", "dev_access")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET", "dev_refresh")
ACCESS_TTL  = int(os.getenv("ACCESS_TTL_SECONDS", "900"))
REFRESH_TTL = int(os.getenv("REFRESH_TTL_SECONDS", "1209600"))
ISS = os.getenv("JWT_ISS", "app")
AUD = os.getenv("JWT_AUD", "frontend")

def _now(): return datetime.now(timezone.utc)

def create_access_token(*, user_id:int, email:str, username:str, roles:list[str]) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "username": username,
        "roles": roles,
        "iat": int(_now().timestamp()),
        "exp": int((_now() + timedelta(seconds=ACCESS_TTL)).timestamp()),
        "iss": ISS, "aud": AUD, "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def create_refresh_token(*, user_id:int) -> str:
    payload = {
        "sub": str(user_id),
        "typ": "refresh",
        "iat": int(_now().timestamp()),
        "exp": int((_now() + timedelta(seconds=REFRESH_TTL)).timestamp()),
        "iss": ISS, "aud": AUD, "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, JWT_REFRESH_SECRET, algorithm="HS256")

def verify_access(token:str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"], audience=AUD, issuer=ISS)

def verify_refresh(token:str) -> dict:
    data = jwt.decode(token, JWT_REFRESH_SECRET, algorithms=["HS256"], audience=AUD, issuer=ISS)
    if data.get("typ") != "refresh":
        raise jwt.InvalidTokenError("Not a refresh token")
    return data