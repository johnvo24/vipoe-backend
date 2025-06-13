from jose import jwt, ExpiredSignatureError, JWTError
from datetime import datetime, timedelta

def create_jwt_token(
    payload: dict,
    secret_key: str,
    algorithm: str = "HS256",
    expires_delta: timedelta | None = None
) -> str:
    data = payload.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        data["exp"] = int(expire.timestamp())
    return jwt.encode(data, secret_key, algorithm=algorithm)

def decode_and_verify_token(
    token: str,
    secret_key: str,
    algorithms: list[str] = ["HS256"]
) -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithms)
        return payload
    except ExpiredSignatureError:
        raise Exception("Token expired")
    except JWTError:
        raise Exception("Invalid token")