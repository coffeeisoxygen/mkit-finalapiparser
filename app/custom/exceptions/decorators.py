from functools import wraps

from app.custom.exceptions.cst_exceptions import AppExceptionError
from app.custom.exceptions.utils import generate_responses


def with_app_exceptions(*exceptions: type[AppExceptionError]):
    """Decorator untuk attach OpenAPI responses otomatis dari exceptions.

    Digunakan di endpoint FastAPI.
    """

    def decorator(func):  # noqa: ANN001
        # attach responses attribute untuk FastAPI
        if not hasattr(func, "responses"):
            func.responses = {}
        func.responses.update(generate_responses(*exceptions))

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
