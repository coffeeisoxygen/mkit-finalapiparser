from app.custom.exceptions.cst_exceptions import AppExceptionError


def generate_responses(*exceptions: type[AppExceptionError]):
    """Buat dictionary responses buat OpenAPI dari AppExceptionError class."""
    res = {}
    for exc in exceptions:
        res[exc.status_code] = {
            "description": exc.default_message,
            "content": {
                "application/json": {
                    "example": {
                        "error": exc.__name__,
                        "message": exc.default_message,
                        "context": {},
                    }
                }
            },
        }
    return res
