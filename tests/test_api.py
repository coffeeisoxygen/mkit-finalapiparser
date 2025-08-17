import schemathesis

schema = schemathesis.openapi.from_url(
    "http://127.0.0.1:8000/openapi.json",
)
# To show the token in the cURL snippet
schema.config.output.sanitization.update(enabled=False)


# @schema.parametrize()
# def test_api(case):
#     case.call_and_validate(headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJBZG1pbiIsImV4cCI6MTc1NTQ0OTM2N30.Nd2M4AYquUZsxAIEp2q9LKu5U7St7b4Bn9IbBPk8kgk"})


@schema.parametrize()
def test_api(case):
    case.call_and_validate()
