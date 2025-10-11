import pytest
import responses

from smoothintegration.exceptions import SIError


class TestCompaniesCreateCompany:

    def test_can_create_company(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.POST,
            "https://api.smooth-integration.com/v1/companies",
            json={
                "message": "Company Created",
                "result": {
                    "name": "Test Company",
                    "id": "11111111-1111-1111-1111-111111111111",
                },
            },
            status=200,
        )

        assert test_client.companies.create_company({"name": "Test Company"}) == {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "Test Company",
        }

    def test_raises_error_on_bad_request(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.POST,
            "https://api.smooth-integration.com/v1/companies",
            json={"message": "Provided Name already exists"},
            status=400,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.companies.create_company({"name": "Test Company"})
        assert str(excinfo.value) == "Bad Request: Provided Name already exists"

    def test_raises_error_on_unauthorized(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.POST,
            "https://api.smooth-integration.com/v1/companies",
            json={"message": "Invalid 'X-Organisation' header"},
            status=401,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.companies.create_company({"name": "Test Company"})
        assert str(excinfo.value) == "Unauthorized: Invalid 'X-Organisation' header"

    def test_raises_error_on_internal_server_error(self, mocked_responses, test_client):
        mocked_responses.add(
            responses.POST,
            "https://api.smooth-integration.com/v1/companies",
            json={"message": "Internal Server Error"},
            status=500,
        )

        with pytest.raises(SIError) as excinfo:
            test_client.companies.create_company({"name": "Test Company"})
        assert str(excinfo.value) == "Internal Server Error"
