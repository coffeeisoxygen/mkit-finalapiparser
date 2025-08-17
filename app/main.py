import uvicorn
from fastapi import FastAPI

from app.custom.cst_lifespan import app_lifespan

app = FastAPI(lifespan=app_lifespan)


if __name__ == "__main__":
    uvicorn.run(
        app="app:main",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,  # Enable auto-reload for development
    )
