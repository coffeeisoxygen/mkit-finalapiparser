from fastapi import APIRouter, Depends, HTTPException, status

from app.deps.deps_auth import DepAuthService
from app.deps.security import get_current_user
from app.schemas.sch_user import Token, User, UserLogin

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/login", response_model=Token)
def login(user_login: UserLogin, auth: DepAuthService):
    """Authenticate user and return JWT token."""
    user = auth.authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = auth.create_access_token(user.username)
    return Token(access_token=token, token_type="bearer")


@router.get("/me", response_model=User)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user
