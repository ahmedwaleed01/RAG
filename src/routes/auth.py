from fastapi import APIRouter, Request, HTTPException, status
from schemas import Credentials
from models import UserModel
from models.db_schemas.user import User
from helpers.security import hash_password, verify_password, create_access_token

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@auth_router.post("/register")
async def register(request: Request, creds: Credentials):
    user_model = await UserModel.create_instance(db_client=request.app.db_client)
    if await user_model.get_user_by_email(creds.email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    user = await user_model.create_user(User(email=creds.email, hashed_password=hash_password(creds.password)))
    return {"access_token": create_access_token({"sub": str(user.id)})}

@auth_router.post("/login")
async def login(request: Request, creds: Credentials):
    user_model = await UserModel.create_instance(db_client=request.app.db_client)
    user = await user_model.get_user_by_email(creds.email)
    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    return {"access_token": create_access_token({"sub": str(user.id)})}