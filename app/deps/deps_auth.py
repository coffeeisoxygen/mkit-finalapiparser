from app.config import get_settings
from app.repositories.rep_user import UserRepository
from app.service.auth_service import AuthService
from app.service.srv_hasher import HasherService


def get_auth_service():
    settings = get_settings()
    user_repo = UserRepository()
    hasher = HasherService()
    return AuthService(
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expire_minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        user_repo=user_repo,
        hasher=hasher,
    )


# Example usage in FastAPI router:
#
# from fastapi import APIRouter, Depends, HTTPException
# from app.schemas.sch_user import UserLogin, Token
#
# router = APIRouter()
#
# @router.post("/login", response_model=Token)
# def login(user_login: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
#     user = auth_service.authenticate_user(user_login.username, user_login.password)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#     token = auth_service.create_access_token({"sub": user.username})
#     return Token(access_token=token, token_type="bearer")
#
# # Protected route example
# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
#
# @router.get("/me")
# def get_me(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)):
#     user = auth_service.get_user_from_token(token)
#     if not user:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     return user
