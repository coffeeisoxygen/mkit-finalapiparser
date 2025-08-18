import schemathesis

# Load OpenAPI dari running FastAPI
schema = schemathesis.openapi.from_url("http://127.0.0.1:8000/openapi.json")

# Jangan sanitize log/token
schema.config.output.sanitization.update(enabled=False)

# Default headers (token valid)
DEFAULT_HEADERS = {"Authorization": "Bearer <token-lo>"}


@schema.parametrize()
def test_api(case, auth_token):
    case.call_and_validate(headers={"Authorization": f"Bearer {auth_token}"})
