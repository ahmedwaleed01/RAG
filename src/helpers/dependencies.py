from fastapi import Request, HTTPException, status, Header
from helpers.security import decode_access_token
from bson.objectid import ObjectId


async def get_current_user_id(request: Request, authorization: str = Header(None)) -> ObjectId:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing or invalid Authorization header")
    payload = decode_access_token(authorization.split(" ", 1)[1])
    if not payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return ObjectId(payload["sub"])