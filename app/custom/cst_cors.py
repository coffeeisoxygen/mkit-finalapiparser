"""setup cors."""

from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    app.add_middleware(
        middleware_class=CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
