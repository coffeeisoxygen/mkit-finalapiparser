import uvicorn
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import register_routers
from app.custom.cst_cors import setup_cors
from app.custom.cst_exceptions import (
    AppExceptionError,
)
from app.custom.cst_lifespan import app_lifespan
from app.custom.cst_middleware import LoggingMiddleware
from app.deps.deps_auth import get_auth_service
from app.service.auth_service import AuthService, UserLogin

app = FastAPI(lifespan=app_lifespan)
app.add_middleware(LoggingMiddleware)
setup_cors(app)
register_routers(app)


# Register exception handlers
@app.exception_handler(AppExceptionError)
async def app_exception_handler(request: Request, exc: AppExceptionError):  # noqa: ARG001, D103, RUF029
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.name,
            "message": exc.message,
            "context": exc.context,
        },
    )


@app.get("/")
async def read_root():  # noqa: D103
    return {"message": "Hello World"}


@app.post("/login")
def login(user_login: UserLogin, auth: AuthService = Depends(get_auth_service)):  # noqa: D103
    return auth.login(user_login)


if __name__ == "__main__":
    uvicorn.run(
        app="app:main",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,  # Enable auto-reload for development
    )
