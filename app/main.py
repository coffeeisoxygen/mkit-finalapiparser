import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# from app.api import register_routers
from app.custom.cst_cors import setup_cors
from app.custom.cst_lifespan import app_lifespan
from app.custom.cst_middleware import LoggingMiddleware
from app.custom.exceptions.cst_exceptions import (
    AppExceptionError,
)

app = FastAPI(lifespan=app_lifespan)
app.add_middleware(LoggingMiddleware)
setup_cors(app)
# register_routers(app)


# Register exception handlers
@app.exception_handler(AppExceptionError)
async def app_exception_handler(request: Request, exc: AppExceptionError):  # noqa: ARG001, D103, RUF029
    return JSONResponse(
        status_code=exc.status_code or 500,
        content=exc.to_dict(),
    )


@app.get("/")
async def read_root():  # noqa: D103
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(
        app="app:main",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,  # Enable auto-reload for development
    )
