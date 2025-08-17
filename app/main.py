import uvicorn
from fastapi import FastAPI

from app.api import register_routers
from app.custom.cst_cors import setup_cors
from app.custom.cst_lifespan import app_lifespan
from app.custom.cst_middleware import LoggingMiddleware

app = FastAPI(lifespan=app_lifespan)
app.add_middleware(LoggingMiddleware)
setup_cors(app)
register_routers(app)


@app.get("/")
async def read_root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(
        app="app:main",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,  # Enable auto-reload for development
    )
